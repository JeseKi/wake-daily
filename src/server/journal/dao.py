# -*- coding: utf-8 -*-
"""觉知日记 DAO。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.dao.dao_base import BaseDAO

from .models import DailyQuestion, JournalEntry, JournalReliefFeedback


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


class JournalEntryDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create(self, *, user_id: int, question_id: int, content: str) -> JournalEntry:
        entry = JournalEntry(
            user_id=user_id,
            question_id=question_id,
            content=content,
        )
        self.db_session.add(entry)
        self.db_session.commit()
        self.db_session.refresh(entry)
        return entry

    def get(self, entry_id: int) -> JournalEntry | None:
        return (
            self.db_session.query(JournalEntry)
            .filter(JournalEntry.id == entry_id)
            .first()
        )

    def list_recent(
        self, *, user_id: int, since: datetime, limit: int = 100
    ) -> list[JournalEntry]:
        return (
            self.db_session.query(JournalEntry)
            .filter(JournalEntry.user_id == user_id)
            .filter(JournalEntry.created_at >= since)
            .order_by(JournalEntry.created_at.desc(), JournalEntry.id.desc())
            .limit(limit)
            .all()
        )


class JournalReliefFeedbackDAO(BaseDAO):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create_if_missing(
        self, *, user_id: int, entry_id: int
    ) -> JournalReliefFeedback | None:
        existing = (
            self.db_session.query(JournalReliefFeedback)
            .filter(JournalReliefFeedback.user_id == user_id)
            .filter(JournalReliefFeedback.entry_id == entry_id)
            .first()
        )
        if existing:
            return None

        feedback = JournalReliefFeedback(user_id=user_id, entry_id=entry_id)
        self.db_session.add(feedback)
        self.db_session.commit()
        self.db_session.refresh(feedback)
        return feedback

    def count_for_entry(self, entry_id: int) -> int:
        return (
            self.db_session.query(func.count(JournalReliefFeedback.id))
            .filter(JournalReliefFeedback.entry_id == entry_id)
            .scalar()
            or 0
        )

    def count_by_entry_ids(self, entry_ids: list[int]) -> dict[int, int]:
        if not entry_ids:
            return {}
        rows = (
            self.db_session.query(
                JournalReliefFeedback.entry_id,
                func.count(JournalReliefFeedback.id),
            )
            .filter(JournalReliefFeedback.entry_id.in_(entry_ids))
            .group_by(JournalReliefFeedback.entry_id)
            .all()
        )
        return {int(entry_id): int(count) for entry_id, count in rows}

    def has_feedback(self, *, user_id: int, entry_id: int) -> bool:
        return (
            self.db_session.query(JournalReliefFeedback.id)
            .filter(JournalReliefFeedback.user_id == user_id)
            .filter(JournalReliefFeedback.entry_id == entry_id)
            .first()
            is not None
        )

    def has_feedback_by_entry_ids(
        self, *, user_id: int, entry_ids: list[int]
    ) -> set[int]:
        if not entry_ids:
            return set()
        rows = (
            self.db_session.query(JournalReliefFeedback.entry_id)
            .filter(JournalReliefFeedback.user_id == user_id)
            .filter(JournalReliefFeedback.entry_id.in_(entry_ids))
            .all()
        )
        return {int(row[0]) for row in rows}

