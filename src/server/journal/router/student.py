# -*- coding: utf-8 -*-
"""觉知日记学生端 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.orm import Session

from src.server.auth.dependencies import get_current_user
from src.server.auth.models import User
from src.server.auth.service.scopes import SCOPE_PROFILE_READ, SCOPE_PROFILE_WRITE
from src.server.dao.dao_base import run_in_thread
from src.server.database import get_db

from .. import service
from ..schemas import (
    AwarenessSessionCreate,
    AwarenessSessionOut,
    DailyQuestionOut,
    GrowthOut,
    InquiryRecordsUpdate,
    JournalBindingOut,
    JournalClassBind,
    JournalEntryCreate,
    JournalEntryOut,
    ReliefFeedbackOut,
    ResonanceFeedbackOut,
    ResonanceItemOut,
)

router = APIRouter(tags=["觉知日记"])


@router.get(
    "/api/journal/today-question",
    response_model=DailyQuestionOut,
    summary="获取今日问题",
)
async def get_today_question(
    db: Session = Depends(get_db),
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
    "/api/journal/me/binding",
    response_model=JournalBindingOut,
    summary="查看我的班级绑定",
)
async def get_my_binding(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _get():
        return service.get_my_binding(db, current_user)

    return await run_in_thread(_get)


@router.post(
    "/api/journal/classes/bind",
    response_model=JournalBindingOut,
    summary="用绑定码加入班级",
)
async def bind_class(
    payload: JournalClassBind,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _bind():
        return service.bind_class(
            db,
            binding_code=payload.binding_code,
            current_user=current_user,
        )

    return await run_in_thread(_bind)


@router.post(
    "/api/journal/sessions",
    response_model=AwarenessSessionOut,
    status_code=status.HTTP_201_CREATED,
    summary="提交三关觉察日记",
)
async def create_awareness_session(
    payload: AwarenessSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _create():
        return service.create_awareness_session(db, payload, current_user)

    return await run_in_thread(_create)


@router.get(
    "/api/journal/sessions/recent",
    response_model=list[AwarenessSessionOut],
    summary="查看我的觉察本",
)
async def list_recent_awareness_sessions(
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _list():
        return service.list_recent_awareness_sessions(
            db,
            current_user=current_user,
            days=days,
        )

    return await run_in_thread(_list)


@router.patch(
    "/api/journal/sessions/{session_id}/inquiries",
    response_model=AwarenessSessionOut,
    summary="保存自由书写追问记录",
)
async def update_awareness_session_inquiries(
    session_id: int,
    payload: InquiryRecordsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _update():
        return service.update_awareness_session_inquiries(
            db,
            session_id=session_id,
            payload=payload,
            current_user=current_user,
        )

    return await run_in_thread(_update)


@router.get(
    "/api/journal/growth",
    response_model=GrowthOut,
    summary="查看我的成长树",
)
async def get_growth(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _get():
        return service.get_growth(db, current_user=current_user)

    return await run_in_thread(_get)


@router.get(
    "/api/journal/resonance",
    response_model=list[ResonanceItemOut],
    summary="查看共振墙",
)
async def list_resonance_items(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_READ]),
):
    def _list():
        return service.list_resonance_items(db, current_user=current_user)

    return await run_in_thread(_list)


@router.post(
    "/api/journal/resonance/{item_id}/empathy",
    response_model=ResonanceFeedbackOut,
    summary="记录我也共鸣",
)
async def create_resonance_feedback(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=[SCOPE_PROFILE_WRITE]),
):
    def _create():
        return service.create_resonance_feedback(
            db,
            item_id=item_id,
            current_user=current_user,
        )

    return await run_in_thread(_create)
