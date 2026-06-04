# -*- coding: utf-8 -*-
"""觉知日记 DAO。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.server.auth.models import User
from src.server.dao.dao_base import BaseDAO

from .models import (
    DailyQuestion,
    JournalAwarenessSession,
    JournalClass,
    JournalClassMembership,
    JournalEntry,
    JournalReliefFeedback,
    JournalResonanceFeedback,
    JournalResonanceItem,
)


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
        return int(self.db_session.query(func.count(JournalClassMembership.id)).scalar() or 0)

    def create(self, *, class_id: int, user_id: int) -> JournalClassMembership:
        item = JournalClassMembership(class_id=class_id, user_id=user_id)
        self.db_session.add(item)
        self.db_session.commit()
        self.db_session.refresh(item)
        return item


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
        return int(self.db_session.query(func.count(JournalAwarenessSession.id)).scalar() or 0)

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

    def get_by_session_id(self, session_id: int) -> JournalResonanceItem | None:
        return (
            self.db_session.query(JournalResonanceItem)
            .filter(JournalResonanceItem.session_id == session_id)
            .first()
        )

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
