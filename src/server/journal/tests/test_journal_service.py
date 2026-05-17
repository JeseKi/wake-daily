# -*- coding: utf-8 -*-
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.server.auth.models import User
from src.server.auth.schemas import UserRole
from src.server.journal.dao import DailyQuestionDAO
from src.server.journal.models import DailyQuestion
from src.server.journal.schemas import (
    DailyQuestionCreate,
    JournalEntryCreate,
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

