# -*- coding: utf-8 -*-
"""普通日记与松一口气反馈服务。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import DailyQuestionDAO, JournalEntryDAO, JournalReliefFeedbackDAO
from ..models import DailyQuestion, JournalEntry
from ..schemas import AttachmentMatchOut, JournalEntryCreate, JournalEntryOut, ReliefFeedbackOut
from .constants import ATTACHMENT_WORDS
from .utils import _normalize_content


def create_entry(
    db: Session, payload: JournalEntryCreate, current_user: User
) -> JournalEntryOut:
    question = DailyQuestionDAO(db).get(payload.question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")

    content = _normalize_content(payload.content)
    entry = JournalEntryDAO(db).create(
        user_id=current_user.id,
        question_id=question.id,
        content=content,
    )
    return _build_entry_out(
        entry,
        question_by_id={question.id: question},
        relief_counts={entry.id: 0},
        user_relief_entry_ids=set(),
    )


def list_recent_entries(
    db: Session, *, current_user: User, days: int = 7
) -> list[JournalEntryOut]:
    resolved_days = max(1, min(days, 30))
    since = datetime.now(timezone.utc) - timedelta(days=resolved_days)
    entries = JournalEntryDAO(db).list_recent(user_id=current_user.id, since=since)
    question_ids = sorted({entry.question_id for entry in entries})
    questions = {
        question.id: question
        for question in (
            DailyQuestionDAO(db).get(question_id) for question_id in question_ids
        )
        if question is not None
    }
    entry_ids = [entry.id for entry in entries]
    feedback_dao = JournalReliefFeedbackDAO(db)
    relief_counts = feedback_dao.count_by_entry_ids(entry_ids)
    user_relief_entry_ids = feedback_dao.has_feedback_by_entry_ids(
        user_id=current_user.id,
        entry_ids=entry_ids,
    )
    return [
        _build_entry_out(
            entry,
            question_by_id=questions,
            relief_counts=relief_counts,
            user_relief_entry_ids=user_relief_entry_ids,
        )
        for entry in entries
    ]


def create_relief_feedback(
    db: Session, *, entry_id: int, current_user: User
) -> ReliefFeedbackOut:
    entry = JournalEntryDAO(db).get(entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="日记不存在")

    feedback_dao = JournalReliefFeedbackDAO(db)
    feedback_dao.create_if_missing(user_id=current_user.id, entry_id=entry_id)
    return ReliefFeedbackOut(
        entry_id=entry_id,
        relief_count=feedback_dao.count_for_entry(entry_id),
        has_relief_feedback=True,
    )


def _find_attachment_matches(content: str) -> list[AttachmentMatchOut]:
    matches: list[AttachmentMatchOut] = []
    for word in ATTACHMENT_WORDS:
        start = content.find(word)
        while start != -1:
            end = start + len(word)
            matches.append(AttachmentMatchOut(word=word, start=start, end=end))
            start = content.find(word, end)
    return sorted(matches, key=lambda item: (item.start, item.word))


def _build_entry_out(
    entry: JournalEntry,
    *,
    question_by_id: dict[int, DailyQuestion],
    relief_counts: dict[int, int],
    user_relief_entry_ids: set[int],
) -> JournalEntryOut:
    question = question_by_id.get(entry.question_id)
    return JournalEntryOut(
        id=entry.id,
        user_id=entry.user_id,
        question_id=entry.question_id,
        question_content=question.content if question else "已删除的问题",
        content=entry.content,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        attachment_matches=_find_attachment_matches(entry.content),
        relief_count=relief_counts.get(entry.id, 0),
        has_relief_feedback=entry.id in user_relief_entry_ids,
    )
