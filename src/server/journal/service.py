# -*- coding: utf-8 -*-
"""觉知日记服务层。"""

from __future__ import annotations

import json
import secrets
import string
from datetime import date, datetime, timedelta, timezone
from typing import NamedTuple

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.server.auth.models import User

from .dao import (
    DailyQuestionDAO,
    JournalAwarenessSessionDAO,
    JournalClassDAO,
    JournalClassMembershipDAO,
    JournalEntryDAO,
    JournalReliefFeedbackDAO,
    JournalResonanceFeedbackDAO,
    JournalResonanceItemDAO,
)
from .models import DailyQuestion, JournalAwarenessSession, JournalClass, JournalEntry
from .schemas import (
    AnalysisMarkOut,
    AdminAwarenessSessionOut,
    AdminDashboardOut,
    AttachmentMatchOut,
    AwarenessSessionCreate,
    AwarenessSessionOut,
    AwarenessSessionReviewUpdate,
    DailyQuestionCreate,
    DailyQuestionUpdate,
    GrowthOut,
    InquiryRecordsUpdate,
    InquiryRecordOut,
    JournalEntryCreate,
    JournalEntryOut,
    JournalBindingOut,
    JournalClassCreate,
    JournalClassOut,
    JournalClassUpdate,
    ObjectivityWarningOut,
    ObjectiveSegmentOut,
    ReliefFeedbackOut,
    ResonanceFeedbackOut,
    ResonanceItemCreate,
    ResonanceItemOut,
)

ENTRY_MODE_AWARENESS = "awareness_v1"
ENTRY_MODE_FREE_REFLECTION = "free_reflection_v1"
ATTACHMENT_WORDS = ("应该", "必须", "不甘心", "非要", "一定", "不能", "凭什么", "早知道")
SUBJECTIVE_WORDS = (
    "觉得",
    "想",
    "认为",
    "无聊",
    "开心",
    "难过",
    "烦躁",
    "感觉",
    "总是",
    "肯定",
    "担心",
    "害怕",
    "希望",
    "讨厌",
    "喜欢",
    "竟然",
    "不负责任",
    "莫名其妙",
)
ANALYSIS_RULES: tuple[tuple[str, str, int], ...] = (
    ("总是", "absolute", 100),
    ("肯定", "absolute", 100),
    ("一定", "absolute", 100),
    ("必须", "absolute", 100),
    ("不能", "absolute", 100),
    ("愤怒", "emotion", 95),
    ("生气", "emotion", 95),
    ("难过", "emotion", 95),
    ("烦躁", "emotion", 95),
    ("害怕", "emotion", 95),
    ("担心", "emotion", 95),
    ("讨厌", "emotion", 95),
    ("喜欢", "emotion", 90),
    ("希望", "emotion", 90),
    ("觉得", "judgment", 80),
    ("认为", "judgment", 80),
    ("不负责任", "judgment", 85),
    ("莫名其妙", "judgment", 85),
    ("我", "self", 70),
)
BINDING_CODE_LENGTH = 8
BINDING_CODE_ALPHABET = string.ascii_uppercase + string.digits
OBJECTIVE_SEGMENT_MESSAGE = "这里更接近事实观察，写得很清楚。"


class AnalysisOccurrence(NamedTuple):
    word: str
    category: str
    start: int
    end: int
    importance: int


def list_daily_questions(db: Session) -> list[DailyQuestion]:
    return DailyQuestionDAO(db).list(include_inactive=True)


def get_today_question(db: Session, today: date | None = None) -> DailyQuestion:
    questions = DailyQuestionDAO(db).list(include_inactive=False)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="还没有可用的每日问题",
        )
    resolved_today = today or datetime.now(timezone.utc).date()
    index = resolved_today.toordinal() % len(questions)
    return questions[index]


def create_daily_question(
    db: Session, payload: DailyQuestionCreate
) -> DailyQuestion:
    content = _normalize_content(payload.content)
    return DailyQuestionDAO(db).create(
        content=content,
        is_active=payload.is_active,
        sort_order=payload.sort_order,
    )


def update_daily_question(
    db: Session, question_id: int, payload: DailyQuestionUpdate
) -> DailyQuestion:
    dao = DailyQuestionDAO(db)
    question = dao.get(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")

    values = payload.model_dump(exclude_unset=True)
    if "content" in values and values["content"] is not None:
        values["content"] = _normalize_content(str(values["content"]))
    return dao.update(question, values)


def delete_daily_question(db: Session, question_id: int) -> None:
    dao = DailyQuestionDAO(db)
    question = dao.get(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    dao.delete(question)


def create_entry(
    db: Session, payload: JournalEntryCreate, current_user: User
) -> JournalEntryOut:
    question = DailyQuestionDAO(db).get(payload.question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")

    content = _normalize_content(payload.content)
    entry = JournalEntryDAO(db).create(
        user_id=current_user.id,
        question_id=question.id,
        content=content,
    )
    return _build_entry_out(
        entry,
        question_by_id={question.id: question},
        relief_counts={entry.id: 0},
        user_relief_entry_ids=set(),
    )


def list_recent_entries(
    db: Session, *, current_user: User, days: int = 7
) -> list[JournalEntryOut]:
    resolved_days = max(1, min(days, 30))
    since = datetime.now(timezone.utc) - timedelta(days=resolved_days)
    entries = JournalEntryDAO(db).list_recent(user_id=current_user.id, since=since)
    question_ids = sorted({entry.question_id for entry in entries})
    questions = {
        question.id: question
        for question in (
            DailyQuestionDAO(db).get(question_id) for question_id in question_ids
        )
        if question is not None
    }
    entry_ids = [entry.id for entry in entries]
    feedback_dao = JournalReliefFeedbackDAO(db)
    relief_counts = feedback_dao.count_by_entry_ids(entry_ids)
    user_relief_entry_ids = feedback_dao.has_feedback_by_entry_ids(
        user_id=current_user.id,
        entry_ids=entry_ids,
    )
    return [
        _build_entry_out(
            entry,
            question_by_id=questions,
            relief_counts=relief_counts,
            user_relief_entry_ids=user_relief_entry_ids,
        )
        for entry in entries
    ]


def create_relief_feedback(
    db: Session, *, entry_id: int, current_user: User
) -> ReliefFeedbackOut:
    entry = JournalEntryDAO(db).get(entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")

    feedback_dao = JournalReliefFeedbackDAO(db)
    feedback_dao.create_if_missing(user_id=current_user.id, entry_id=entry_id)
    return ReliefFeedbackOut(
        entry_id=entry_id,
        relief_count=feedback_dao.count_for_entry(entry_id),
        has_relief_feedback=True,
    )


def list_classes(db: Session) -> list[JournalClass]:
    return JournalClassDAO(db).list(include_inactive=True)


def create_class(
    db: Session, payload: JournalClassCreate, current_user: User
) -> JournalClass:
    name = _normalize_content(payload.name)
    dao = JournalClassDAO(db)
    for _ in range(10):
        binding_code = _generate_binding_code()
        try:
            return dao.create(
                name=name,
                binding_code=binding_code,
                created_by_user_id=current_user.id,
                is_active=payload.is_active,
            )
        except IntegrityError:
            db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="绑定码生成失败，请重试",
    )


def update_class(
    db: Session, class_id: int, payload: JournalClassUpdate
) -> JournalClass:
    dao = JournalClassDAO(db)
    journal_class = dao.get(class_id)
    if not journal_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    values = payload.model_dump(exclude_unset=True)
    if "name" in values and values["name"] is not None:
        values["name"] = _normalize_content(str(values["name"]))
    return dao.update(journal_class, values)


def regenerate_class_binding_code(db: Session, class_id: int) -> JournalClass:
    dao = JournalClassDAO(db)
    journal_class = dao.get(class_id)
    if not journal_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    for _ in range(10):
        try:
            return dao.update(journal_class, {"binding_code": _generate_binding_code()})
        except IntegrityError:
            db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="绑定码生成失败，请重试",
    )


def get_my_binding(db: Session, current_user: User) -> JournalBindingOut:
    membership = JournalClassMembershipDAO(db).get_by_user_id(current_user.id)
    if not membership:
        return JournalBindingOut(is_bound=False, class_info=None)

    journal_class = JournalClassDAO(db).get(membership.class_id)
    if not journal_class:
        return JournalBindingOut(is_bound=False, class_info=None)
    return JournalBindingOut(
        is_bound=True,
        class_info=JournalClassOut.model_validate(journal_class),
    )


def bind_class(db: Session, *, binding_code: str, current_user: User) -> JournalBindingOut:
    normalized_code = binding_code.strip().upper()
    if not normalized_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="绑定码不能为空")

    membership_dao = JournalClassMembershipDAO(db)
    existing = membership_dao.get_by_user_id(current_user.id)
    if existing:
        journal_class = JournalClassDAO(db).get(existing.class_id)
        return JournalBindingOut(
            is_bound=True,
            class_info=(
                JournalClassOut.model_validate(journal_class)
                if journal_class
                else None
            ),
        )

    journal_class = JournalClassDAO(db).get_by_binding_code(normalized_code)
    if not journal_class or not journal_class.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定码无效")

    membership_dao.create(class_id=journal_class.id, user_id=current_user.id)
    return JournalBindingOut(
        is_bound=True,
        class_info=JournalClassOut.model_validate(journal_class),
    )


def create_awareness_session(
    db: Session,
    payload: AwarenessSessionCreate,
    current_user: User,
    today: date | None = None,
) -> AwarenessSessionOut:
    membership = JournalClassMembershipDAO(db).get_by_user_id(current_user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先绑定班级")

    resolved_today = today or datetime.now(timezone.utc).date()
    if payload.content is not None:
        content = _normalize_content(payload.content)
        analysis_marks = analyze_free_content(content)
        warnings = evaluate_objectivity([content])
        try:
            session = JournalAwarenessSessionDAO(db).create(
                user_id=current_user.id,
                class_id=membership.class_id,
                entry_mode=ENTRY_MODE_FREE_REFLECTION,
                free_content=content,
                objective_events_json=_json_dumps([content]),
                selected_event_index=0,
                emotion_label="自由书写",
                emotion_note="自由书写",
                present_anchor="自由书写",
                objectivity_warnings_json=_json_dumps(
                    [warning.model_dump() for warning in warnings]
                ),
                analysis_marks_json=_json_dumps(
                    [mark.model_dump() for mark in analysis_marks]
                ),
                inquiry_records_json="[]",
                submitted_on=resolved_today,
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="今天已经提交过觉察日记",
            )
        return _build_awareness_session_out(session)

    events = [_normalize_content(item) for item in (payload.objective_events or [])]
    selected_event_index = payload.selected_event_index or 0
    if selected_event_index >= len(events):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="触动事件不在客观记录范围内",
        )

    warnings = evaluate_objectivity(events)
    try:
        session = JournalAwarenessSessionDAO(db).create(
            user_id=current_user.id,
            class_id=membership.class_id,
            entry_mode=ENTRY_MODE_AWARENESS,
            objective_events_json=_json_dumps(events),
            selected_event_index=selected_event_index,
            emotion_label=_normalize_content(payload.emotion_label or ""),
            emotion_note=_normalize_content(payload.emotion_note or ""),
            present_anchor=_normalize_content(payload.present_anchor or ""),
            objectivity_warnings_json=_json_dumps(
                [warning.model_dump() for warning in warnings]
            ),
            submitted_on=resolved_today,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="今天已经提交过觉察日记",
        )
    return _build_awareness_session_out(session)


def list_recent_awareness_sessions(
    db: Session, *, current_user: User, days: int = 30
) -> list[AwarenessSessionOut]:
    resolved_days = max(1, min(days, 90))
    since = datetime.now(timezone.utc) - timedelta(days=resolved_days)
    sessions = JournalAwarenessSessionDAO(db).list_recent(
        user_id=current_user.id,
        since=since,
    )
    return [_build_awareness_session_out(item) for item in sessions]


def list_admin_awareness_sessions(
    db: Session, *, class_id: int | None = None
) -> list[AdminAwarenessSessionOut]:
    rows = JournalAwarenessSessionDAO(db).list_admin(class_id=class_id)
    resonance_dao = JournalResonanceItemDAO(db)
    items = []
    for session, student, journal_class in rows:
        resonance_item = resonance_dao.get_by_session_id(session.id, active_only=True)
        items.append(
            _build_admin_awareness_session_out(
                session,
                student=student,
                journal_class=journal_class,
                resonance_item_id=resonance_item.id if resonance_item else None,
            )
        )
    return items


def update_awareness_session_review(
    db: Session,
    *,
    session_id: int,
    payload: AwarenessSessionReviewUpdate,
    current_user: User,
) -> AwarenessSessionOut:
    dao = JournalAwarenessSessionDAO(db)
    session = dao.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")

    values: dict[str, object] = payload.model_dump(exclude_unset=True)
    if session.entry_mode == ENTRY_MODE_FREE_REFLECTION:
        values = {
            "review_comment": values.get("review_comment"),
        }
    review_comment = values.get("review_comment")
    if isinstance(review_comment, str):
        values["review_comment"] = review_comment.strip() or None
    reward_label = values.get("reward_label")
    if isinstance(reward_label, str):
        values["reward_label"] = reward_label.strip() or None
    values["reviewed_by_user_id"] = current_user.id
    values["reviewed_at"] = datetime.now(timezone.utc)
    return _build_awareness_session_out(dao.update(session, values))


def update_awareness_session_inquiries(
    db: Session,
    *,
    session_id: int,
    payload: InquiryRecordsUpdate,
    current_user: User,
) -> AwarenessSessionOut:
    dao = JournalAwarenessSessionDAO(db)
    session = dao.get(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")
    if session.entry_mode != ENTRY_MODE_FREE_REFLECTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有自由书写日记可以保存追问记录",
        )

    valid_mark_ids = {
        str(mark.get("id"))
        for mark in _json_loads_list(session.analysis_marks_json)
        if isinstance(mark, dict) and mark.get("id")
    }
    records = []
    for record in payload.records:
        if record.mark_id not in valid_mark_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="追问标记不存在",
            )
        values = record.model_dump(mode="json")
        if values.get("answer") is not None:
            answer = str(values["answer"]).strip()
            values["answer"] = answer or None
        records.append(values)

    return _build_awareness_session_out(
        dao.update(session, {"inquiry_records_json": _json_dumps(records)})
    )


def get_growth(db: Session, *, current_user: User) -> GrowthOut:
    sessions = JournalAwarenessSessionDAO(db).list_all_for_growth(user_id=current_user.id)
    submitted_dates = sorted({item.submitted_on for item in sessions}, reverse=True)
    streak = _calculate_streak(submitted_dates, datetime.now(timezone.utc).date())
    total = len(submitted_dates)
    return GrowthOut(
        streak_days=streak,
        total_sessions=total,
        tree_stage=_tree_stage_for_streak(streak),
        badges=_badges_for_sessions(sessions, streak),
    )


def create_resonance_item(
    db: Session,
    *,
    session_id: int,
    payload: ResonanceItemCreate,
    current_user: User,
) -> ResonanceItemOut:
    session = JournalAwarenessSessionDAO(db).get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")

    item_dao = JournalResonanceItemDAO(db)
    existing = item_dao.get_by_session_id(session_id)
    if existing and existing.is_active:
        return _build_resonance_item_out(
            db,
            existing,
            current_user_id=current_user.id,
        )

    events = _json_loads(session.objective_events_json, [])
    default_excerpt = session.free_content or session.present_anchor or session.emotion_note
    if isinstance(events, list) and events:
        default_excerpt = str(events[min(session.selected_event_index, len(events) - 1)])
    excerpt = (payload.excerpt or default_excerpt).strip()
    if not excerpt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="收录内容不能为空")

    if existing:
        item = item_dao.update(
            existing,
            {
                "excerpt": excerpt,
                "created_by_user_id": current_user.id,
                "is_active": True,
            },
        )
        return _build_resonance_item_out(db, item, current_user_id=current_user.id)

    item = item_dao.create(
        session_id=session.id,
        class_id=session.class_id,
        source_user_id=session.user_id,
        created_by_user_id=current_user.id,
        excerpt=excerpt,
    )
    return _build_resonance_item_out(db, item, current_user_id=current_user.id)


def list_resonance_items(
    db: Session, *, current_user: User
) -> list[ResonanceItemOut]:
    membership = JournalClassMembershipDAO(db).get_by_user_id(current_user.id)
    if not membership:
        return []
    class_id = membership.class_id
    items = JournalResonanceItemDAO(db).list_active(class_id=class_id)
    return [
        _build_resonance_item_out(db, item, current_user_id=current_user.id)
        for item in items
    ]


def delete_resonance_item(db: Session, *, item_id: int) -> None:
    item = JournalResonanceItemDAO(db).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="共振片段不存在")
    JournalResonanceItemDAO(db).set_active(item, False)


def create_resonance_feedback(
    db: Session, *, item_id: int, current_user: User
) -> ResonanceFeedbackOut:
    item = JournalResonanceItemDAO(db).get(item_id)
    if not item or not item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="共振片段不存在")
    membership = JournalClassMembershipDAO(db).get_by_user_id(current_user.id)
    if not membership or membership.class_id != item.class_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="共振片段不存在")

    feedback_dao = JournalResonanceFeedbackDAO(db)
    feedback_dao.create_if_missing(user_id=current_user.id, item_id=item_id)
    return ResonanceFeedbackOut(
        item_id=item_id,
        empathy_count=feedback_dao.count_for_item(item_id),
        has_empathy_feedback=True,
    )


def get_admin_dashboard(db: Session) -> AdminDashboardOut:
    class_count = len(JournalClassDAO(db).list(include_inactive=True))
    student_count = JournalClassMembershipDAO(db).count_students()
    session_dao = JournalAwarenessSessionDAO(db)
    submitted_today_count = session_dao.count_submitted_on(
        datetime.now(timezone.utc).date()
    )
    submission_rate = (
        round(submitted_today_count / student_count, 4) if student_count else 0.0
    )
    return AdminDashboardOut(
        class_count=class_count,
        student_count=student_count,
        submitted_today_count=submitted_today_count,
        submission_rate=submission_rate,
        total_sessions=session_dao.count_total(),
        resonance_count=JournalResonanceItemDAO(db).count_active(),
        emotion_counts=session_dao.emotion_counts(),
    )


def evaluate_objectivity(events: list[str]) -> list[ObjectivityWarningOut]:
    warnings: list[ObjectivityWarningOut] = []
    for index, event in enumerate(events):
        if "我" in event:
            warnings.append(
                ObjectivityWarningOut(
                    event_index=index,
                    word="我",
                    message="请尝试使用第三人称视角，避免使用“我”。",
                )
            )
        for word in SUBJECTIVE_WORDS:
            if word in event:
                warnings.append(
                    ObjectivityWarningOut(
                        event_index=index,
                        word=word,
                        message=f"检测到主观词“{word}”，请确认是否在描述事实。",
                    )
                )
    return warnings


def analyze_free_content(content: str) -> list[AnalysisMarkOut]:
    occurrences: list[AnalysisOccurrence] = []
    for word, category, importance in ANALYSIS_RULES:
        start = content.find(word)
        while start != -1:
            occurrences.append(
                AnalysisOccurrence(
                    word=word,
                    category=category,
                    start=start,
                    end=start + len(word),
                    importance=importance,
                )
            )
            start = content.find(word, start + len(word))

    occurrences.sort(key=lambda item: (item.start, item.word))
    top_keys: set[tuple[int, int, str]] = set()
    top_signatures: set[tuple[str, str]] = set()
    for item in sorted(
        occurrences,
        key=lambda item: (-item.importance, item.start),
    ):
        signature = (item.word, item.category)
        if signature in top_signatures:
            continue
        top_signatures.add(signature)
        top_keys.add((item.start, item.end, item.word))
        if len(top_keys) >= 3:
            break
    return [
        AnalysisMarkOut(
            id=f"m{index}",
            word=item.word,
            category=item.category,
            start=item.start,
            end=item.end,
            importance=item.importance,
            question=_question_for_mark(item.word, item.category),
            is_top=(
                item.start,
                item.end,
                item.word,
            )
            in top_keys,
        )
        for index, item in enumerate(occurrences, start=1)
    ]


def normalize_top_analysis_marks(
    marks: list[AnalysisMarkOut],
) -> list[AnalysisMarkOut]:
    top_ids: set[str] = set()
    top_signatures: set[tuple[str, str]] = set()
    for mark in sorted(marks, key=lambda item: (-item.importance, item.start)):
        signature = (mark.word, mark.category)
        if signature in top_signatures:
            continue
        top_signatures.add(signature)
        top_ids.add(mark.id)
        if len(top_ids) >= 3:
            break
    return [mark.model_copy(update={"is_top": mark.id in top_ids}) for mark in marks]


def build_objective_segments(
    content: str, marks: list[AnalysisMarkOut]
) -> list[ObjectiveSegmentOut]:
    if not content:
        return []
    marked_ranges = [(mark.start, mark.end) for mark in marks]
    segments: list[ObjectiveSegmentOut] = []
    cursor = 0
    for index, char in enumerate(content):
        if char not in "。！？!?；;\n":
            continue
        _append_objective_segment(content, cursor, index + 1, marked_ranges, segments)
        cursor = index + 1
    _append_objective_segment(content, cursor, len(content), marked_ranges, segments)
    return segments


def _append_objective_segment(
    content: str,
    start: int,
    end: int,
    marked_ranges: list[tuple[int, int]],
    segments: list[ObjectiveSegmentOut],
) -> None:
    raw = content[start:end]
    stripped = raw.strip()
    if not stripped:
        return
    leading_space = len(raw) - len(raw.lstrip())
    trailing_space = len(raw.rstrip())
    segment_start = start + leading_space
    segment_end = start + trailing_space
    has_mark = any(
        mark_start < segment_end and mark_end > segment_start
        for mark_start, mark_end in marked_ranges
    )
    if not has_mark:
        segments.append(
            ObjectiveSegmentOut(
                text=stripped,
                start=segment_start,
                end=segment_end,
                message=OBJECTIVE_SEGMENT_MESSAGE,
            )
        )


def _question_for_mark(word: str, category: str) -> str:
    if category == "self":
        return f"当你写下“{word}”时，你最想被看见的是什么？"
    if category == "absolute":
        return f"这个“{word}”背后，你在守护什么？"
    if category == "emotion":
        return f"这个“{word}”出现时，它在提醒你哪个需要？"
    return f"如果先放下“{word}”这个判断，你真正希望发生什么？"


def _normalize_content(content: str) -> str:
    normalized = content.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容不能为空",
        )
    return normalized


def _generate_binding_code() -> str:
    return "".join(
        secrets.choice(BINDING_CODE_ALPHABET) for _ in range(BINDING_CODE_LENGTH)
    )


def _json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _json_loads(raw: str, fallback: object) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def _json_loads_list(raw: str) -> list[object]:
    value = _json_loads(raw, [])
    return value if isinstance(value, list) else []


def _build_awareness_session_out(
    session: JournalAwarenessSession,
) -> AwarenessSessionOut:
    warnings = _json_loads_list(session.objectivity_warnings_json)
    analysis_marks = [
        AnalysisMarkOut.model_validate(item)
        for item in _json_loads_list(session.analysis_marks_json)
        if isinstance(item, dict)
    ]
    analysis_marks = normalize_top_analysis_marks(analysis_marks)
    inquiry_records = [
        InquiryRecordOut.model_validate(item)
        for item in _json_loads_list(session.inquiry_records_json)
        if isinstance(item, dict)
    ]
    free_content = session.free_content
    if session.entry_mode == ENTRY_MODE_FREE_REFLECTION and free_content is None:
        events = _json_loads_list(session.objective_events_json)
        free_content = str(events[0]) if events else None
    return AwarenessSessionOut(
        id=session.id,
        user_id=session.user_id,
        class_id=session.class_id,
        entry_mode=session.entry_mode,
        free_content=free_content,
        objective_events=[str(item) for item in _json_loads_list(session.objective_events_json)],
        selected_event_index=session.selected_event_index,
        emotion_label=session.emotion_label,
        emotion_note=session.emotion_note,
        present_anchor=session.present_anchor,
        objectivity_warnings=[
            ObjectivityWarningOut.model_validate(item)
            for item in warnings
            if isinstance(item, dict)
        ],
        analysis_marks=analysis_marks,
        inquiry_records=inquiry_records,
        objective_segments=build_objective_segments(free_content or "", analysis_marks),
        submitted_on=session.submitted_on,
        review_score=session.review_score,
        review_comment=session.review_comment,
        reward_label=session.reward_label,
        reviewed_by_user_id=session.reviewed_by_user_id,
        reviewed_at=session.reviewed_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _build_admin_awareness_session_out(
    session: JournalAwarenessSession,
    *,
    student: User,
    journal_class: JournalClass,
    resonance_item_id: int | None,
) -> AdminAwarenessSessionOut:
    base = _build_awareness_session_out(session).model_dump()
    return AdminAwarenessSessionOut(
        **base,
        student_username=student.username,
        student_name=student.name,
        class_name=journal_class.name,
        is_collected_to_resonance=resonance_item_id is not None,
        resonance_item_id=resonance_item_id,
    )


def _build_resonance_item_out(
    db: Session,
    item,
    *,
    current_user_id: int,
) -> ResonanceItemOut:
    feedback_dao = JournalResonanceFeedbackDAO(db)
    has_feedback = item.id in feedback_dao.has_feedback_by_item_ids(
        user_id=current_user_id,
        item_ids=[item.id],
    )
    return ResonanceItemOut(
        id=item.id,
        session_id=item.session_id,
        class_id=item.class_id,
        excerpt=item.excerpt,
        empathy_count=feedback_dao.count_for_item(item.id),
        has_empathy_feedback=has_feedback,
        created_at=item.created_at,
    )


def _calculate_streak(submitted_dates: list[date], today: date) -> int:
    if not submitted_dates:
        return 0
    date_set = set(submitted_dates)
    cursor = today
    if cursor not in date_set:
        cursor = today - timedelta(days=1)
    streak = 0
    while cursor in date_set:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def _tree_stage_for_streak(streak: int) -> str:
    if streak >= 14:
        return "开花"
    if streak >= 7:
        return "大树"
    if streak >= 3:
        return "小树"
    if streak >= 1:
        return "幼苗"
    return "种子"


def _badges_for_sessions(
    sessions: list[JournalAwarenessSession], streak: int
) -> list[str]:
    badges: list[str] = []
    if sessions:
        badges.append("首次完成三关觉察")
    if streak >= 3:
        badges.append("连续三天照见")
    if streak >= 7:
        badges.append("一周安静生长")
    emotion_counts: dict[str, int] = {}
    for session in sessions:
        emotion_counts[session.emotion_label] = emotion_counts.get(session.emotion_label, 0) + 1
    if any(count >= 2 for count in emotion_counts.values()):
        badges.append("首次精准标记重复情绪")
    return badges


def _find_attachment_matches(content: str) -> list[AttachmentMatchOut]:
    matches: list[AttachmentMatchOut] = []
    for word in ATTACHMENT_WORDS:
        start = content.find(word)
        while start != -1:
            end = start + len(word)
            matches.append(AttachmentMatchOut(word=word, start=start, end=end))
            start = content.find(word, end)
    return sorted(matches, key=lambda item: (item.start, item.word))


def _build_entry_out(
    entry: JournalEntry,
    *,
    question_by_id: dict[int, DailyQuestion],
    relief_counts: dict[int, int],
    user_relief_entry_ids: set[int],
) -> JournalEntryOut:
    question = question_by_id.get(entry.question_id)
    return JournalEntryOut(
        id=entry.id,
        user_id=entry.user_id,
        question_id=entry.question_id,
        question_content=question.content if question else "已删除的问题",
        content=entry.content,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        attachment_matches=_find_attachment_matches(entry.content),
        relief_count=relief_counts.get(entry.id, 0),
        has_relief_feedback=entry.id in user_relief_entry_ids,
    )
