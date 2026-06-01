"""add awareness journal v1 tables

Revision ID: 20260601_0002
Revises: 20260517_0001
Create Date: 2026-06-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260601_0002"
down_revision = "20260517_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "journal_classes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("binding_code", sa.String(length=32), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("binding_code", name="uq_journal_classes_binding_code"),
    )
    op.create_index("ix_journal_classes_binding_code", "journal_classes", ["binding_code"])
    op.create_index(
        "ix_journal_classes_created_by_user_id",
        "journal_classes",
        ["created_by_user_id"],
    )

    op.create_table(
        "journal_class_memberships",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_journal_class_memberships_user"),
        sa.UniqueConstraint(
            "class_id",
            "user_id",
            name="uq_journal_class_memberships_class_user",
        ),
    )
    op.create_index(
        "ix_journal_class_memberships_class_id",
        "journal_class_memberships",
        ["class_id"],
    )
    op.create_index(
        "ix_journal_class_memberships_user_id",
        "journal_class_memberships",
        ["user_id"],
    )

    op.create_table(
        "journal_awareness_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("objective_events_json", sa.Text(), nullable=False),
        sa.Column("selected_event_index", sa.Integer(), nullable=False),
        sa.Column("emotion_label", sa.String(length=50), nullable=False),
        sa.Column("emotion_note", sa.Text(), nullable=False),
        sa.Column("present_anchor", sa.Text(), nullable=False),
        sa.Column("objectivity_warnings_json", sa.Text(), nullable=False),
        sa.Column("submitted_on", sa.Date(), nullable=False),
        sa.Column("review_score", sa.Integer(), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("reward_label", sa.String(length=120), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "submitted_on",
            name="uq_journal_awareness_sessions_user_date",
        ),
    )
    op.create_index(
        "ix_journal_awareness_sessions_user_id",
        "journal_awareness_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_journal_awareness_sessions_class_id",
        "journal_awareness_sessions",
        ["class_id"],
    )
    op.create_index(
        "ix_journal_awareness_sessions_submitted_on",
        "journal_awareness_sessions",
        ["submitted_on"],
    )
    op.create_index(
        "ix_journal_awareness_sessions_created_at",
        "journal_awareness_sessions",
        ["created_at"],
    )

    op.create_table(
        "journal_resonance_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("source_user_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", name="uq_journal_resonance_items_session"),
    )
    op.create_index(
        "ix_journal_resonance_items_session_id",
        "journal_resonance_items",
        ["session_id"],
    )
    op.create_index(
        "ix_journal_resonance_items_class_id",
        "journal_resonance_items",
        ["class_id"],
    )
    op.create_index(
        "ix_journal_resonance_items_source_user_id",
        "journal_resonance_items",
        ["source_user_id"],
    )
    op.create_index(
        "ix_journal_resonance_items_created_by_user_id",
        "journal_resonance_items",
        ["created_by_user_id"],
    )

    op.create_table(
        "journal_resonance_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "user_id",
            "item_id",
            name="uq_journal_resonance_feedback_user_item",
        ),
    )
    op.create_index(
        "ix_journal_resonance_feedback_user_id",
        "journal_resonance_feedback",
        ["user_id"],
    )
    op.create_index(
        "ix_journal_resonance_feedback_item_id",
        "journal_resonance_feedback",
        ["item_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_journal_resonance_feedback_item_id",
        table_name="journal_resonance_feedback",
    )
    op.drop_index(
        "ix_journal_resonance_feedback_user_id",
        table_name="journal_resonance_feedback",
    )
    op.drop_table("journal_resonance_feedback")
    op.drop_index(
        "ix_journal_resonance_items_created_by_user_id",
        table_name="journal_resonance_items",
    )
    op.drop_index(
        "ix_journal_resonance_items_source_user_id",
        table_name="journal_resonance_items",
    )
    op.drop_index(
        "ix_journal_resonance_items_class_id",
        table_name="journal_resonance_items",
    )
    op.drop_index(
        "ix_journal_resonance_items_session_id",
        table_name="journal_resonance_items",
    )
    op.drop_table("journal_resonance_items")
    op.drop_index(
        "ix_journal_awareness_sessions_created_at",
        table_name="journal_awareness_sessions",
    )
    op.drop_index(
        "ix_journal_awareness_sessions_submitted_on",
        table_name="journal_awareness_sessions",
    )
    op.drop_index(
        "ix_journal_awareness_sessions_class_id",
        table_name="journal_awareness_sessions",
    )
    op.drop_index(
        "ix_journal_awareness_sessions_user_id",
        table_name="journal_awareness_sessions",
    )
    op.drop_table("journal_awareness_sessions")
    op.drop_index(
        "ix_journal_class_memberships_user_id",
        table_name="journal_class_memberships",
    )
    op.drop_index(
        "ix_journal_class_memberships_class_id",
        table_name="journal_class_memberships",
    )
    op.drop_table("journal_class_memberships")
    op.drop_index(
        "ix_journal_classes_created_by_user_id",
        table_name="journal_classes",
    )
    op.drop_index("ix_journal_classes_binding_code", table_name="journal_classes")
    op.drop_table("journal_classes")
