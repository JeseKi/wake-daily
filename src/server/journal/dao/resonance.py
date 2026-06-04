# -*- coding: utf-8 -*-
"""共振片段与反馈 DAO。"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO

from ..models import JournalResonanceFeedback, JournalResonanceItem


class JournalResonanceItemDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(
        self,
        *,
        session_id: int,
        class_id: int,
        source_user_id: int,
        created_by_user_id: int,
        excerpt: str,
    ) -> JournalResonanceItem:
        item = JournalResonanceItem(
            session_id=session_id,
            class_id=class_id,
            source_user_id=source_user_id,
            created_by_user_id=created_by_user_id,
            excerpt=excerpt,
        )
        self.db_session.add(item)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item

    def get(self, item_id: int) -> JournalResonanceItem | None:
        return (
            self.db_session.query(JournalResonanceItem)
            .filter(JournalResonanceItem.id == item_id)
            .first()
        )

    def get_by_session_id(
        self, session_id: int, *, active_only: bool = False
    ) -> JournalResonanceItem | None:
        query = self.db_session.query(JournalResonanceItem).filter(
            JournalResonanceItem.session_id == session_id
        )
        if active_only:
            query = query.filter(JournalResonanceItem.is_active.is_(True))
        return query.first()

    def list_active(
        self, *, class_id: int | None = None, limit: int = 100
    ) -> list[JournalResonanceItem]:
        query = self.db_session.query(JournalResonanceItem).filter(
            JournalResonanceItem.is_active.is_(True)
        )
        if class_id is not None:
            query = query.filter(JournalResonanceItem.class_id == class_id)
        return (
            query.order_by(
                JournalResonanceItem.created_at.desc(),
                JournalResonanceItem.id.desc(),
            )
            .limit(limit)
            .all()
        )

    def count_active(self) -> int:
        return int(
            self.db_session.query(func.count(JournalResonanceItem.id))
            .filter(JournalResonanceItem.is_active.is_(True))
            .scalar()
            or 0
        )

    def set_active(self, item: JournalResonanceItem, is_active: bool) -> None:
        item.is_active = is_active
        self.db_session.commit()

    def update(
        self, item: JournalResonanceItem, values: dict[str, object]
    ) -> JournalResonanceItem:
        for key, value in values.items():
            setattr(item, key, value)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item


class JournalResonanceFeedbackDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create_if_missing(
        self, *, user_id: int, item_id: int
    ) -> JournalResonanceFeedback | None:
        existing = (
            self.db_session.query(JournalResonanceFeedback)
            .filter(JournalResonanceFeedback.user_id == user_id)
            .filter(JournalResonanceFeedback.item_id == item_id)
            .first()
        )
        if existing:
            return None

        feedback = JournalResonanceFeedback(user_id=user_id, item_id=item_id)
        self.db_session.add(feedback)
        self.db_session.commit()
        self.db_session.refresh(feedback)
        return feedback

    def count_for_item(self, item_id: int) -> int:
        return int(
            self.db_session.query(func.count(JournalResonanceFeedback.id))
            .filter(JournalResonanceFeedback.item_id == item_id)
            .scalar()
            or 0
        )

    def count_by_item_ids(self, item_ids: list[int]) -> dict[int, int]:
        if not item_ids:
            return {}
        rows = (
            self.db_session.query(
                JournalResonanceFeedback.item_id,
                func.count(JournalResonanceFeedback.id),
            )
            .filter(JournalResonanceFeedback.item_id.in_(item_ids))
            .group_by(JournalResonanceFeedback.item_id)
            .all()
        )
        return {int(item_id): int(count) for item_id, count in rows}

    def has_feedback_by_item_ids(self, *, user_id: int, item_ids: list[int]) -> set[int]:
        if not item_ids:
            return set()
        rows = (
            self.db_session.query(JournalResonanceFeedback.item_id)
            .filter(JournalResonanceFeedback.user_id == user_id)
            .filter(JournalResonanceFeedback.item_id.in_(item_ids))
            .all()
        )
        return {int(row[0]) for row in rows}
