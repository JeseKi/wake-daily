# -*- coding: utf-8 -*-
"""班级与成员 DAO。"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO

from ..models import JournalClass, JournalClassMembership


class JournalClassDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def list(self, *, include_inactive: bool = True) -> list[JournalClass]:
        query = self.db_session.query(JournalClass)
        if not include_inactive:
            query = query.filter(JournalClass.is_active.is_(True))
        return query.order_by(JournalClass.created_at.desc(), JournalClass.id.desc()).all()

    def get(self, class_id: int) -> JournalClass | None:
        return (
            self.db_session.query(JournalClass)
            .filter(JournalClass.id == class_id)
            .first()
        )

    def get_by_binding_code(self, binding_code: str) -> JournalClass | None:
        return (
            self.db_session.query(JournalClass)
            .filter(JournalClass.binding_code == binding_code)
            .first()
        )

    def create(
        self,
        *,
        name: str,
        binding_code: str,
        created_by_user_id: int,
        is_active: bool,
    ) -> JournalClass:
        item = JournalClass(
            name=name,
            binding_code=binding_code,
            created_by_user_id=created_by_user_id,
            is_active=is_active,
        )
        self.db_session.add(item)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item

    def update(self, item: JournalClass, values: dict[str, object]) -> JournalClass:
        for key, value in values.items():
            setattr(item, key, value)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item


class JournalClassMembershipDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def get_by_user_id(self, user_id: int) -> JournalClassMembership | None:
        return (
            self.db_session.query(JournalClassMembership)
            .filter(JournalClassMembership.user_id == user_id)
            .first()
        )

    def count_students(self) -> int:
        return int(
            self.db_session.query(func.count(JournalClassMembership.id)).scalar() or 0
        )

    def create(self, *, class_id: int, user_id: int) -> JournalClassMembership:
        item = JournalClassMembership(class_id=class_id, user_id=user_id)
        self.db_session.add(item)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item
