# -*- coding: utf-8 -*-
"""共振片段与共情反馈服务。"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import (
    JournalAwarenessSessionDAO,
    JournalClassMembershipDAO,
    JournalResonanceFeedbackDAO,
    JournalResonanceItemDAO,
)
from ..schemas import (
    ResonanceFeedbackOut,
    ResonanceItemCreate,
    ResonanceItemOut,
)
from .serializers import _build_resonance_item_out
from .utils import _json_loads


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
