"""add free reflection journal fields

Revision ID: 20260604_0003
Revises: 20260601_0002
Create Date: 2026-06-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260604_0003"
down_revision = "20260601_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "journal_awareness_sessions",
        sa.Column(
            "entry_mode",
            sa.String(length=32),
            nullable=False,
            server_default="awareness_v1",
        ),
    )
    op.add_column(
        "journal_awareness_sessions",
        sa.Column("free_content", sa.Text(), nullable=True),
    )
    op.add_column(
        "journal_awareness_sessions",
        sa.Column(
            "analysis_marks_json",
            sa.Text(),
            nullable=False,
            server_default="[]",
        ),
    )
    op.add_column(
        "journal_awareness_sessions",
        sa.Column(
            "inquiry_records_json",
            sa.Text(),
            nullable=False,
            server_default="[]",
        ),
    )
    op.create_index(
        "ix_journal_awareness_sessions_entry_mode",
        "journal_awareness_sessions",
        ["entry_mode"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_journal_awareness_sessions_entry_mode",
        table_name="journal_awareness_sessions",
    )
    op.drop_column("journal_awareness_sessions", "inquiry_records_json")
    op.drop_column("journal_awareness_sessions", "analysis_marks_json")
    op.drop_column("journal_awareness_sessions", "free_content")
    op.drop_column("journal_awareness_sessions", "entry_mode")
