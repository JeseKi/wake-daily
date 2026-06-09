# -*- coding: utf-8 -*-
"""觉察日记提交、追问与老师回应服务。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import JournalAwarenessSessionDAO, JournalClassMembershipDAO
from ..models import JournalAwarenessSession
from ..schemas import (
    AwarenessSessionCreate,
    AwarenessSessionOut,
    AwarenessSessionReviewUpdate,
    InquiryRecordsUpdate,
)
from .analysis import analyze_free_content, evaluate_objectivity
from .constants import ENTRY_MODE_AWARENESS, ENTRY_MODE_FREE_REFLECTION
from .serializers import _build_awareness_session_out
from .utils import _json_dumps, _json_loads_list, _normalize_content


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
    dao = JournalAwarenessSessionDAO(db)
    existing_session = dao.get_by_user_and_date(
        user_id=current_user.id,
        submitted_on=resolved_today,
    )
    if payload.content is not None:
        return _create_free_reflection_session(
            db,
            payload=payload,
            current_user=current_user,
            class_id=membership.class_id,
            submitted_on=resolved_today,
            existing_session=existing_session,
        )
    return _create_legacy_awareness_session(
        db,
        payload=payload,
        current_user=current_user,
        class_id=membership.class_id,
        submitted_on=resolved_today,
        existing_session=existing_session,
    )


def _create_free_reflection_session(
    db: Session,
    *,
    payload: AwarenessSessionCreate,
    current_user: User,
    class_id: int,
    submitted_on: date,
    existing_session: JournalAwarenessSession | None = None,
) -> AwarenessSessionOut:
    content = _normalize_content(payload.content or "")
    analysis_marks = analyze_free_content(content)
    warnings = evaluate_objectivity([content])
    values = {
        "class_id": class_id,
        "entry_mode": ENTRY_MODE_FREE_REFLECTION,
        "free_content": content,
        "objective_events_json": _json_dumps([content]),
        "selected_event_index": 0,
        "emotion_label": "自由书写",
        "emotion_note": "自由书写",
        "present_anchor": "自由书写",
        "objectivity_warnings_json": _json_dumps(
            [warning.model_dump() for warning in warnings]
        ),
        "analysis_marks_json": _json_dumps(
            [mark.model_dump() for mark in analysis_marks]
        ),
        "inquiry_records_json": "[]",
    }
    dao = JournalAwarenessSessionDAO(db)
    if existing_session:
        return _build_awareness_session_out(dao.update(existing_session, values))

    try:
        session = dao.create(
            user_id=current_user.id,
            submitted_on=submitted_on,
            **values,
        )
    except IntegrityError:
        db.rollback()
        session = dao.get_by_user_and_date(
            user_id=current_user.id,
            submitted_on=submitted_on,
        )
        if not session:
            raise
        session = dao.update(session, values)
    return _build_awareness_session_out(session)


def _create_legacy_awareness_session(
    db: Session,
    *,
    payload: AwarenessSessionCreate,
    current_user: User,
    class_id: int,
    submitted_on: date,
    existing_session: JournalAwarenessSession | None = None,
) -> AwarenessSessionOut:
    events = [_normalize_content(item) for item in (payload.objective_events or [])]
    selected_event_index = payload.selected_event_index or 0
    if selected_event_index >= len(events):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="触动事件不在客观记录范围内",
        )

    warnings = evaluate_objectivity(events)
    values = {
        "class_id": class_id,
        "entry_mode": ENTRY_MODE_AWARENESS,
        "free_content": None,
        "objective_events_json": _json_dumps(events),
        "selected_event_index": selected_event_index,
        "emotion_label": _normalize_content(payload.emotion_label or ""),
        "emotion_note": _normalize_content(payload.emotion_note or ""),
        "present_anchor": _normalize_content(payload.present_anchor or ""),
        "objectivity_warnings_json": _json_dumps(
            [warning.model_dump() for warning in warnings]
        ),
        "analysis_marks_json": "[]",
        "inquiry_records_json": "[]",
    }
    dao = JournalAwarenessSessionDAO(db)
    if existing_session:
        return _build_awareness_session_out(dao.update(existing_session, values))

    try:
        session = dao.create(
            user_id=current_user.id,
            submitted_on=submitted_on,
            **values,
        )
    except IntegrityError:
        db.rollback()
        session = dao.get_by_user_and_date(
            user_id=current_user.id,
            submitted_on=submitted_on,
        )
        if not session:
            raise
        session = dao.update(session, values)
    return _build_awareness_session_out(session)


def get_today_awareness_session(
    db: Session,
    *,
    current_user: User,
    today: date | None = None,
) -> AwarenessSessionOut | None:
    resolved_today = today or datetime.now(timezone.utc).date()
    session = JournalAwarenessSessionDAO(db).get_by_user_and_date(
        user_id=current_user.id,
        submitted_on=resolved_today,
    )
    return _build_awareness_session_out(session) if session else None


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
        values = {"review_comment": values.get("review_comment")}
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
