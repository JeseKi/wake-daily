# -*- coding: utf-8 -*-
"""觉知日记管理端 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.server.auth.dependencies import get_current_admin, get_current_admin_writer
from src.server.auth.models import User
from src.server.database import get_db

from .. import service
from ..schemas import (
    AdminAwarenessSessionOut,
    AdminDashboardOut,
    AwarenessSessionOut,
    AwarenessSessionReviewUpdate,
    DailyQuestionCreate,
    DailyQuestionOut,
    DailyQuestionUpdate,
    JournalClassCreate,
    JournalClassOut,
    JournalClassUpdate,
    ResonanceItemCreate,
    ResonanceItemOut,
)

router = APIRouter(tags=["觉知日记"])


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
