# -*- coding: utf-8 -*-
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.server.auth.models import User
from src.server.auth.schemas import UserRole
from src.server.journal.dao import DailyQuestionDAO
from src.server.journal.models import DailyQuestion
from src.server.journal.schemas import (
    AwarenessSessionCreate,
    AwarenessSessionReviewUpdate,
    DailyQuestionCreate,
    InquiryRecordsUpdate,
    InquiryRecordUpdate,
    JournalClassCreate,
    JournalEntryCreate,
    ResonanceItemCreate,
)
from src.server.journal import service


def _create_user(db: Session, username: str, user_id: int | None = None) -> User:
    user = User(
        id=user_id,
        username=username,
        email=f"{username}@example.com",
        name=username,
        role=UserRole.USER,
    )
    user.set_password("Password123")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_today_question_rotates_by_date(test_db_session: Session):
    dao = DailyQuestionDAO(test_db_session)
    first = dao.create(content="第一个问题", is_active=True, sort_order=10)
    second = dao.create(content="第二个问题", is_active=True, sort_order=20)

    today = date(2026, 5, 17)
    expected = [first, second][today.toordinal() % 2]

    assert service.get_today_question(test_db_session, today=today).id == expected.id


def test_today_question_requires_active_question(test_db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        service.get_today_question(test_db_session, today=date(2026, 5, 17))

    assert exc_info.value.status_code == 404


def test_create_entry_validates_content_and_highlights_words(test_db_session: Session):
    user = _create_user(test_db_session, "journal_user")
    question = service.create_daily_question(
        test_db_session,
        DailyQuestionCreate(content="今天写点什么？", sort_order=10),
    )

    entry = service.create_entry(
        test_db_session,
        JournalEntryCreate(
            question_id=question.id,
            content="我应该慢一点，但也不必非要立刻想明白。",
        ),
        user,
    )

    assert entry.question_content == "今天写点什么？"
    assert [match.word for match in entry.attachment_matches] == ["应该", "非要"]
    assert entry.relief_count == 0
    assert entry.has_relief_feedback is False

    with pytest.raises(HTTPException) as exc_info:
        service.create_entry(
            test_db_session,
            JournalEntryCreate(question_id=question.id, content="   "),
            user,
        )
    assert exc_info.value.status_code == 400


def test_recent_entries_are_user_scoped_and_relief_is_idempotent(
    test_db_session: Session,
):
    user = _create_user(test_db_session, "recent_user")
    other_user = _create_user(test_db_session, "other_recent_user")
    question = DailyQuestionDAO(test_db_session).create(
        content="今天有什么念头？",
        is_active=True,
        sort_order=10,
    )

    entry = service.create_entry(
        test_db_session,
        JournalEntryCreate(question_id=question.id, content="我必须完成这件事"),
        user,
    )
    service.create_entry(
        test_db_session,
        JournalEntryCreate(question_id=question.id, content="别人日记"),
        other_user,
    )

    first_feedback = service.create_relief_feedback(
        test_db_session,
        entry_id=entry.id,
        current_user=user,
    )
    second_feedback = service.create_relief_feedback(
        test_db_session,
        entry_id=entry.id,
        current_user=user,
    )

    recent = service.list_recent_entries(test_db_session, current_user=user, days=7)

    assert first_feedback.relief_count == 1
    assert second_feedback.relief_count == 1
    assert [item.id for item in recent] == [entry.id]
    assert recent[0].relief_count == 1
    assert recent[0].has_relief_feedback is True

    with pytest.raises(HTTPException) as exc_info:
        service.create_relief_feedback(
            test_db_session,
            entry_id=entry.id,
            current_user=other_user,
        )
    assert exc_info.value.status_code == 404


def test_deleted_question_keeps_entry_readable(test_db_session: Session):
    user = _create_user(test_db_session, "deleted_question_user")
    question = DailyQuestionDAO(test_db_session).create(
        content="临时问题",
        is_active=True,
        sort_order=10,
    )
    entry = service.create_entry(
        test_db_session,
        JournalEntryCreate(question_id=question.id, content="保留内容"),
        user,
    )

    test_db_session.delete(test_db_session.get(DailyQuestion, question.id))
    test_db_session.commit()

    recent = service.list_recent_entries(test_db_session, current_user=user, days=7)

    assert recent[0].id == entry.id
    assert recent[0].question_content == "已删除的问题"


def test_awareness_session_binding_growth_and_resonance(test_db_session: Session):
    teacher = _create_user(test_db_session, "teacher_user")
    student = _create_user(test_db_session, "student_user")

    journal_class = service.create_class(
        test_db_session,
        JournalClassCreate(name="清晨一班"),
        teacher,
    )
    binding = service.bind_class(
        test_db_session,
        binding_code=journal_class.binding_code,
        current_user=student,
    )
    assert binding.is_bound is True
    assert binding.class_info is not None
    assert binding.class_info.name == "清晨一班"

    session = service.create_awareness_session(
        test_db_session,
        AwarenessSessionCreate(
            objective_events=["我觉得他总是第一个到教室", "她把书放在桌上"],
            selected_event_index=0,
            emotion_label="焦虑",
            emotion_note="看到同学先完成时，身体变紧。",
            present_anchor="窗台上有一滴水。",
        ),
        student,
        today=datetime.now(timezone.utc).date(),
    )

    assert session.class_id == journal_class.id
    assert [item.word for item in session.objectivity_warnings] == ["我", "觉得", "总是"]

    reviewed = service.update_awareness_session_review(
        test_db_session,
        session_id=session.id,
        payload=AwarenessSessionReviewUpdate(
            review_score=4,
            review_comment="记录清楚。",
            reward_label="观察清晰",
        ),
        current_user=teacher,
    )
    assert reviewed.review_score == 4
    assert reviewed.reward_label == "观察清晰"

    resonance = service.create_resonance_item(
        test_db_session,
        session_id=session.id,
        payload=ResonanceItemCreate(excerpt=None),
        current_user=teacher,
    )
    feedback = service.create_resonance_feedback(
        test_db_session,
        item_id=resonance.id,
        current_user=student,
    )
    repeat_feedback = service.create_resonance_feedback(
        test_db_session,
        item_id=resonance.id,
        current_user=student,
    )

    growth = service.get_growth(test_db_session, current_user=student)

    assert feedback.empathy_count == 1
    assert repeat_feedback.empathy_count == 1
    assert growth.streak_days == 1
    assert growth.tree_stage == "幼苗"
    assert "首次完成三关觉察" in growth.badges


def test_free_reflection_marks_inquiries_and_response(test_db_session: Session):
    teacher = _create_user(test_db_session, "free_teacher")
    student = _create_user(test_db_session, "free_student")
    journal_class = service.create_class(
        test_db_session,
        JournalClassCreate(name="自由书写班"),
        teacher,
    )
    service.bind_class(
        test_db_session,
        binding_code=journal_class.binding_code,
        current_user=student,
    )

    session = service.create_awareness_session(
        test_db_session,
        AwarenessSessionCreate(content="我觉得他总是不理我。窗边有一小块光。"),
        student,
        today=date(2026, 6, 4),
    )

    assert session.entry_mode == "free_reflection_v1"
    assert session.free_content == "我觉得他总是不理我。窗边有一小块光。"
    assert {mark.word for mark in session.analysis_marks if mark.is_top} == {
        "总是",
        "觉得",
        "我",
    }
    assert session.objective_segments[0].text == "窗边有一小块光。"

    updated = service.update_awareness_session_inquiries(
        test_db_session,
        session_id=session.id,
        payload=InquiryRecordsUpdate(
            records=[
                InquiryRecordUpdate(
                    mark_id=session.analysis_marks[0].id,
                    question=session.analysis_marks[0].question,
                    answer="我想被认真听见。",
                )
            ]
        ),
        current_user=student,
    )
    assert updated.inquiry_records[0].answer == "我想被认真听见。"

    reviewed = service.update_awareness_session_review(
        test_db_session,
        session_id=session.id,
        payload=AwarenessSessionReviewUpdate(
            review_score=5,
            review_comment="我看见你在努力靠近真实感受。",
            reward_label="不会保存",
        ),
        current_user=teacher,
    )
    assert reviewed.review_comment == "我看见你在努力靠近真实感受。"
    assert reviewed.review_score is None
    assert reviewed.reward_label is None


def test_free_reflection_deduplicates_repeated_top_words():
    marks = service.analyze_free_content("我不知道我为什么要做这个东西。")

    assert [mark.word for mark in marks] == ["我", "我"]
    assert [mark.word for mark in marks if mark.is_top] == ["我"]
