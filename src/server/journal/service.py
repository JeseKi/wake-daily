# -*- coding: utf-8 -*-
"""觉知日记服务层。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.server.auth.models import User

from .dao import DailyQuestionDAO, JournalEntryDAO, JournalReliefFeedbackDAO
from .models import DailyQuestion, JournalEntry
from .schemas import (
    DailyQuestionCreate,
    DailyQuestionUpdate,
    JournalEntryCreate,
    JournalEntryOut,
    ReliefFeedbackOut,
)

ATTACHMENT_WORDS = ("应该", "必须", "不甘心", "非要", "一定", "不能", "凭什么", "早知道")


def list_daily_questions(db: Session) -> list[DailyQuestion]:
    return DailyQuestionDAO(db).list(include_inactive=True)


def get_today_question(db: Session, today: date | None = None) -> DailyQuestion:
    questions = DailyQuestionDAO(db).list(include_inactive=False)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="还没有可用的每日问题",
        )
    resolved_today = today or datetime.now(timezone.utc).date()
    index = resolved_today.toordinal() % len(questions)
    return questions[index]


def create_daily_question(
    db: Session, payload: DailyQuestionCreate
) -> DailyQuestion:
    content = _normalize_content(payload.content)
    return DailyQuestionDAO(db).create(
        content=content,
        is_active=payload.is_active,
        sort_order=payload.sort_order,
    )


def update_daily_question(
    db: Session, question_id: int, payload: DailyQuestionUpdate
) -> DailyQuestion:
    dao = DailyQuestionDAO(db)
    question = dao.get(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")

    values = payload.model_dump(exclude_unset=True)
    if "content" in values and values["content"] is not None:
        values["content"] = _normalize_content(str(values["content"]))
    return dao.update(question, values)


def delete_daily_question(db: Session, question_id: int) -> None:
    dao = DailyQuestionDAO(db)
    question = dao.get(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="问题不存在")
    dao.delete(question)


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


def _normalize_content(content: str) -> str:
    normalized = content.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容不能为空",
        )
    return normalized


def _find_attachment_matches(content: str) -> list[dict[str, int | str]]:
    matches: list[dict[str, int | str]] = []
    for word in ATTACHMENT_WORDS:
        start = content.find(word)
        while start != -1:
            end = start + len(word)
            matches.append({"word": word, "start": start, "end": end})
            start = content.find(word, end)
    return sorted(matches, key=lambda item: (int(item["start"]), str(item["word"])))


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

