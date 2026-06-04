# -*- coding: utf-8 -*-
"""每日问题 DAO。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO

from ..models import DailyQuestion


class DailyQuestionDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def list(self, *, include_inactive: bool = True) -> list[DailyQuestion]:
        query = self.db_session.query(DailyQuestion)
        if not include_inactive:
            query = query.filter(DailyQuestion.is_active.is_(True))
        return query.order_by(DailyQuestion.sort_order.asc(), DailyQuestion.id.asc()).all()

    def get(self, question_id: int) -> DailyQuestion | None:
        return (
            self.db_session.query(DailyQuestion)
            .filter(DailyQuestion.id == question_id)
            .first()
        )

    def create(
        self, *, content: str, is_active: bool, sort_order: int
    ) -> DailyQuestion:
        question = DailyQuestion(
            content=content,
            is_active=is_active,
            sort_order=sort_order,
        )
        self.db_session.add(question)
        self.db_session.commit()
        self.db_session.refresh(question)
        return question

    def update(self, question: DailyQuestion, values: dict[str, object]) -> DailyQuestion:
        for key, value in values.items():
            setattr(question, key, value)
        self.db_session.commit()
        self.db_session.refresh(question)
        return question

    def delete(self, question: DailyQuestion) -> None:
        self.db_session.delete(question)
        self.db_session.commit()
