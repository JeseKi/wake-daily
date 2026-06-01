# -*- coding: utf-8 -*-
"""
觉知日记业务模型。

说明：
- 与模板示例模块保持一致，不使用 ORM relationship。
- 跨表关联由服务层通过 id 手动校验。
"""

from __future__ import annotations

from datetime import datetime, timezone

from datetime import date

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.server.database import Base


class DailyQuestion(Base):
    __tablename__ = "daily_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class JournalReliefFeedback(Base):
    __tablename__ = "journal_relief_feedback"
    __table_args__ = (
        UniqueConstraint("user_id", "entry_id", name="uq_journal_relief_user_entry"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    entry_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class JournalClass(Base):
    __tablename__ = "journal_classes"
    __table_args__ = (
        UniqueConstraint("binding_code", name="uq_journal_classes_binding_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    binding_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class JournalClassMembership(Base):
    __tablename__ = "journal_class_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_journal_class_memberships_user"),
        UniqueConstraint(
            "class_id",
            "user_id",
            name="uq_journal_class_memberships_class_user",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class JournalAwarenessSession(Base):
    __tablename__ = "journal_awareness_sessions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "submitted_on",
            name="uq_journal_awareness_sessions_user_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    objective_events_json: Mapped[str] = mapped_column(Text, nullable=False)
    selected_event_index: Mapped[int] = mapped_column(Integer, nullable=False)
    emotion_label: Mapped[str] = mapped_column(String(50), nullable=False)
    emotion_note: Mapped[str] = mapped_column(Text, nullable=False)
    present_anchor: Mapped[str] = mapped_column(Text, nullable=False)
    objectivity_warnings_json: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_on: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    review_score: Mapped[int | None] = mapped_column(Integer, default=None)
    review_comment: Mapped[str | None] = mapped_column(Text, default=None)
    reward_label: Mapped[str | None] = mapped_column(String(120), default=None)
    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, default=None)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class JournalResonanceItem(Base):
    __tablename__ = "journal_resonance_items"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_journal_resonance_items_session"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    source_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class JournalResonanceFeedback(Base):
    __tablename__ = "journal_resonance_feedback"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "item_id",
            name="uq_journal_resonance_feedback_user_item",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
