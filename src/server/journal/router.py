# -*- coding: utf-8 -*-
"""觉知日记 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from src.server.auth.dependencies import get_current_admin, get_current_admin_writer
from src.server.auth.dependencies import get_current_user
from src.server.auth.models import User
from src.server.auth.service.scopes import SCOPE_PROFILE_READ, SCOPE_PROFILE_WRITE
from src.server.dao.dao_base import run_in_thread
from src.server.database import get_db

from . import service
from .schemas import (
    DailyQuestionCreate,
    DailyQuestionOut,
    DailyQuestionUpdate,
    JournalEntryCreate,
    JournalEntryOut,
    ReliefFeedbackOut,
)

router = APIRouter(tags=["觉知日记"])


@router.get(
    "/api/journal/today-question",
    response_model=DailyQuestionOut,
    summary="获取今日问题",
)
async def get_today_question(
    db: Session = Depends(get_db),
    _: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _get():
        return service.get_today_question(db)

    return await run_in_thread(_get)


@router.post(
    "/api/journal/entries",
    response_model=JournalEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="保存日记",
)
async def create_entry(
    payload: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _create():
        return service.create_entry(db, payload, current_user)

    return await run_in_thread(_create)


@router.get(
    "/api/journal/entries/recent",
    response_model=list[JournalEntryOut],
    summary="查看最近日记",
)
async def list_recent_entries(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _list():
        return service.list_recent_entries(db, current_user=current_user, days=days)

    return await run_in_thread(_list)


@router.post(
    "/api/journal/entries/{entry_id}/relief",
    response_model=ReliefFeedbackOut,
    summary="记录松动反馈",
)
async def create_relief_feedback(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _create():
        return service.create_relief_feedback(
            db,
            entry_id=entry_id,
            current_user=current_user,
        )

    return await run_in_thread(_create)


@router.get(
    "/api/admin/journal/questions",
    response_model=list[DailyQuestionOut],
    summary="管理员查看每日问题",
)
async def admin_list_daily_questions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return service.list_daily_questions(db)


@router.post(
    "/api/admin/journal/questions",
    response_model=DailyQuestionOut,
    status_code=status.HTTP_201_CREATED,
    summary="管理员新增每日问题",
)
async def admin_create_daily_question(
    payload: DailyQuestionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    return service.create_daily_question(db, payload)


@router.patch(
    "/api/admin/journal/questions/{question_id}",
    response_model=DailyQuestionOut,
    summary="管理员更新每日问题",
)
async def admin_update_daily_question(
    question_id: int,
    payload: DailyQuestionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    return service.update_daily_question(db, question_id, payload)


@router.delete(
    "/api/admin/journal/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="管理员删除每日问题",
)
async def admin_delete_daily_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    service.delete_daily_question(db, question_id)

