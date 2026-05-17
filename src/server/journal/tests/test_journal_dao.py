# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.server.journal.dao import (
    DailyQuestionDAO,
    JournalEntryDAO,
    JournalReliefFeedbackDAO,
)


def test_daily_question_dao_crud(test_db_session: Session):
    dao = DailyQuestionDAO(test_db_session)

    question = dao.create(content="今天看见了什么？", is_active=True, sort_order=20)
    assert question.id is not None
    assert question.content == "今天看见了什么？"

    updated = dao.update(question, {"content": "今天放下了什么？", "is_active": False})
    assert updated.content == "今天放下了什么？"
    assert updated.is_active is False

    assert dao.get(updated.id) is not None
    assert dao.list(include_inactive=False) == []

    dao.delete(updated)
    assert dao.get(question.id) is None


def test_journal_entry_recent_and_feedback_dao(test_db_session: Session):
    question = DailyQuestionDAO(test_db_session).create(
        content="今天有什么念头？",
        is_active=True,
        sort_order=10,
    )
    entry_dao = JournalEntryDAO(test_db_session)
    feedback_dao = JournalReliefFeedbackDAO(test_db_session)

    old_entry = entry_dao.create(user_id=1, question_id=question.id, content="旧内容")
    old_entry.created_at = datetime.now(timezone.utc) - timedelta(days=10)
    test_db_session.commit()

    recent_entry = entry_dao.create(
        user_id=1,
        question_id=question.id,
        content="我应该慢一点",
    )
    other_user_entry = entry_dao.create(
        user_id=2,
        question_id=question.id,
        content="别人内容",
    )

    recent_entries = entry_dao.list_recent(
        user_id=1,
        since=datetime.now(timezone.utc) - timedelta(days=7),
    )
    assert [entry.id for entry in recent_entries] == [recent_entry.id]

    created = feedback_dao.create_if_missing(user_id=1, entry_id=recent_entry.id)
    duplicate = feedback_dao.create_if_missing(user_id=1, entry_id=recent_entry.id)
    feedback_dao.create_if_missing(user_id=2, entry_id=other_user_entry.id)

    assert created is not None
    assert duplicate is None
    assert feedback_dao.count_for_entry(recent_entry.id) == 1
    assert feedback_dao.count_by_entry_ids([recent_entry.id, other_user_entry.id]) == {
        recent_entry.id: 1,
        other_user_entry.id: 1,
    }
    assert feedback_dao.has_feedback(user_id=1, entry_id=recent_entry.id) is True
    assert feedback_dao.has_feedback_by_entry_ids(
        user_id=1,
        entry_ids=[recent_entry.id, other_user_entry.id],
    ) == {recent_entry.id}

