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
    AdminAwarenessSessionOut,
    AdminDashboardOut,
    AwarenessSessionCreate,
    AwarenessSessionOut,
    AwarenessSessionReviewUpdate,
    DailyQuestionCreate,
    DailyQuestionOut,
    DailyQuestionUpdate,
    GrowthOut,
    InquiryRecordsUpdate,
    JournalEntryCreate,
    JournalEntryOut,
    JournalBindingOut,
    JournalClassBind,
    JournalClassCreate,
    JournalClassOut,
    JournalClassUpdate,
    ReliefFeedbackOut,
    ResonanceFeedbackOut,
    ResonanceItemCreate,
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


@router.get(
    "/api/admin/journal/classes",
    response_model=list[JournalClassOut],
    summary="管理员查看班级",
)
async def admin_list_classes(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return service.list_classes(db)


@router.post(
    "/api/admin/journal/classes",
    response_model=JournalClassOut,
    status_code=status.HTTP_201_CREATED,
    summary="管理员创建班级",
)
async def admin_create_class(
    payload: JournalClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_writer),
):
    return service.create_class(db, payload, current_user)


@router.patch(
    "/api/admin/journal/classes/{class_id}",
    response_model=JournalClassOut,
    summary="管理员更新班级",
)
async def admin_update_class(
    class_id: int,
    payload: JournalClassUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    return service.update_class(db, class_id, payload)


@router.post(
    "/api/admin/journal/classes/{class_id}/regenerate-code",
    response_model=JournalClassOut,
    summary="管理员重置班级绑定码",
)
async def admin_regenerate_class_code(
    class_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    return service.regenerate_class_binding_code(db, class_id)


@router.get(
    "/api/admin/journal/sessions",
    response_model=list[AdminAwarenessSessionOut],
    summary="管理员查看三关日记",
)
async def admin_list_awareness_sessions(
    class_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return service.list_admin_awareness_sessions(db, class_id=class_id)


@router.patch(
    "/api/admin/journal/sessions/{session_id}/review",
    response_model=AwarenessSessionOut,
    summary="管理员批阅三关日记",
)
async def admin_review_awareness_session(
    session_id: int,
    payload: AwarenessSessionReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_writer),
):
    return service.update_awareness_session_review(
        db,
        session_id=session_id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/api/admin/journal/sessions/{session_id}/resonance",
    response_model=ResonanceItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="管理员匿名收录到共振墙",
)
async def admin_create_resonance_item(
    session_id: int,
    payload: ResonanceItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_writer),
):
    return service.create_resonance_item(
        db,
        session_id=session_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/api/admin/journal/resonance/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="管理员下架共振墙片段",
)
async def admin_delete_resonance_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_writer),
):
    service.delete_resonance_item(db, item_id=item_id)


@router.get(
    "/api/admin/journal/dashboard",
    response_model=AdminDashboardOut,
    summary="管理员查看觉察日记数据看板",
)
async def admin_get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return service.get_admin_dashboard(db)
