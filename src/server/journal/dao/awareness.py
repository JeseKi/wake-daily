# -*- coding: utf-8 -*-
"""觉察日记 DAO。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.auth.models import User
from src.server.dao.dao_base import BaseDAO

from ..models import JournalAwarenessSession, JournalClass


class JournalAwarenessSessionDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(
        self,
        *,
        user_id: int,
        class_id: int,
        objective_events_json: str,
        selected_event_index: int,
        emotion_label: str,
        emotion_note: str,
        present_anchor: str,
        objectivity_warnings_json: str,
        submitted_on: date,
        entry_mode: str = "awareness_v1",
        free_content: str | None = None,
        analysis_marks_json: str = "[]",
        inquiry_records_json: str = "[]",
    ) -> JournalAwarenessSession:
        item = JournalAwarenessSession(
            user_id=user_id,
            class_id=class_id,
            entry_mode=entry_mode,
            free_content=free_content,
            objective_events_json=objective_events_json,
            selected_event_index=selected_event_index,
            emotion_label=emotion_label,
            emotion_note=emotion_note,
            present_anchor=present_anchor,
            objectivity_warnings_json=objectivity_warnings_json,
            analysis_marks_json=analysis_marks_json,
            inquiry_records_json=inquiry_records_json,
            submitted_on=submitted_on,
        )
        self.db_session.add(item)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item

    def get(self, session_id: int) -> JournalAwarenessSession | None:
        return (
            self.db_session.query(JournalAwarenessSession)
            .filter(JournalAwarenessSession.id == session_id)
            .first()
        )

    def get_by_user_and_date(
        self, *, user_id: int, submitted_on: date
    ) -> JournalAwarenessSession | None:
        return (
            self.db_session.query(JournalAwarenessSession)
            .filter(JournalAwarenessSession.user_id == user_id)
            .filter(JournalAwarenessSession.submitted_on == submitted_on)
            .first()
        )

    def list_recent(
        self, *, user_id: int, since: datetime, limit: int = 100
    ) -> list[JournalAwarenessSession]:
        return (
            self.db_session.query(JournalAwarenessSession)
            .filter(JournalAwarenessSession.user_id == user_id)
            .filter(JournalAwarenessSession.created_at >= since)
            .order_by(
                JournalAwarenessSession.created_at.desc(),
                JournalAwarenessSession.id.desc(),
            )
            .limit(limit)
            .all()
        )

    def list_admin(
        self,
        *,
        class_id: int | None = None,
        limit: int = 200,
    ) -> list[tuple[JournalAwarenessSession, User, JournalClass]]:
        query = (
            self.db_session.query(JournalAwarenessSession, User, JournalClass)
            .join(User, User.id == JournalAwarenessSession.user_id)
            .join(JournalClass, JournalClass.id == JournalAwarenessSession.class_id)
        )
        if class_id is not None:
            query = query.filter(JournalAwarenessSession.class_id == class_id)
        rows = (
            query.order_by(
                JournalAwarenessSession.created_at.desc(),
                JournalAwarenessSession.id.desc(),
            )
            .limit(limit)
            .all()
        )
        return [(row[0], row[1], row[2]) for row in rows]

    def list_all_for_growth(self, *, user_id: int) -> list[JournalAwarenessSession]:
        return (
            self.db_session.query(JournalAwarenessSession)
            .filter(JournalAwarenessSession.user_id == user_id)
            .order_by(JournalAwarenessSession.submitted_on.desc())
            .all()
        )

    def count_total(self) -> int:
        return int(
            self.db_session.query(func.count(JournalAwarenessSession.id)).scalar() or 0
        )

    def count_submitted_on(self, submitted_on: date) -> int:
        return int(
            self.db_session.query(func.count(JournalAwarenessSession.id))
            .filter(JournalAwarenessSession.submitted_on == submitted_on)
            .scalar()
            or 0
        )

    def emotion_counts(self) -> dict[str, int]:
        rows = (
            self.db_session.query(
                JournalAwarenessSession.emotion_label,
                func.count(JournalAwarenessSession.id),
            )
            .group_by(JournalAwarenessSession.emotion_label)
            .all()
        )
        return {str(label): int(count) for label, count in rows}

    def update(
        self, item: JournalAwarenessSession, values: dict[str, object]
    ) -> JournalAwarenessSession:
        for key, value in values.items():
            setattr(item, key, value)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item
