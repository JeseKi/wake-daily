# -*- coding: utf-8 -*-
"""每日问题服务。"""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..dao import DailyQuestionDAO
from ..models import DailyQuestion
from ..schemas import DailyQuestionCreate, DailyQuestionUpdate
from .utils import _normalize_content


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
