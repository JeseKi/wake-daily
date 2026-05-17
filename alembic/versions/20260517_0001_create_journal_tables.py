"""create journal tables

Revision ID: 20260517_0001
Revises:
Create Date: 2026-05-17
"""

from __future__ import annotations

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "20260517_0001"
down_revision = None
branch_labels = None
depends_on = None


DEFAULT_DAILY_QUESTIONS = (
    "今天有什么念头反复来找你？",
    "今天哪一刻，你发现自己又在用力证明什么？",
    "如果不用急着变好，今天你最想诚实写下什么？",
    "今天你对自己说了哪个“应该”？",
    "此刻有什么事情，其实可以先轻轻放一放？",
    "今天哪个不甘心，让你多停留了一会儿？",
    "如果把答案放慢一点，你现在最真实的感受是什么？",
)


def upgrade() -> None:
    op.create_table(
        "daily_questions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("content", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_journal_entries_user_id", "journal_entries", ["user_id"])
    op.create_index("ix_journal_entries_question_id", "journal_entries", ["question_id"])
    op.create_index("ix_journal_entries_created_at", "journal_entries", ["created_at"])

    op.create_table(
        "journal_relief_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "entry_id", name="uq_journal_relief_user_entry"),
    )
    op.create_index(
        "ix_journal_relief_feedback_user_id",
        "journal_relief_feedback",
        ["user_id"],
    )
    op.create_index(
        "ix_journal_relief_feedback_entry_id",
        "journal_relief_feedback",
        ["entry_id"],
    )

    now = datetime.now(timezone.utc)
    questions_table = sa.table(
        "daily_questions",
        sa.column("content", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("sort_order", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        questions_table,
        [
            {
                "content": content,
                "is_active": True,
                "sort_order": index * 10,
                "created_at": now,
                "updated_at": now,
            }
            for index, content in enumerate(DEFAULT_DAILY_QUESTIONS, start=1)
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_journal_relief_feedback_entry_id", table_name="journal_relief_feedback")
    op.drop_index("ix_journal_relief_feedback_user_id", table_name="journal_relief_feedback")
    op.drop_table("journal_relief_feedback")
    op.drop_index("ix_journal_entries_created_at", table_name="journal_entries")
    op.drop_index("ix_journal_entries_question_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_user_id", table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_table("daily_questions")

