# -*- coding: utf-8 -*-
"""班级与学生绑定服务。"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import JournalClassDAO, JournalClassMembershipDAO
from ..models import JournalClass
from ..schemas import (
    JournalBindingOut,
    JournalClassCreate,
    JournalClassOut,
    JournalClassUpdate,
)
from .utils import _generate_binding_code, _normalize_content


def list_classes(db: Session) -> list[JournalClass]:
    return JournalClassDAO(db).list(include_inactive=True)


def create_class(
    db: Session, payload: JournalClassCreate, current_user: User
) -> JournalClass:
    name = _normalize_content(payload.name)
    dao = JournalClassDAO(db)
    for _ in range(10):
        binding_code = _generate_binding_code()
        try:
            return dao.create(
                name=name,
                binding_code=binding_code,
                created_by_user_id=current_user.id,
                is_active=payload.is_active,
            )
        except IntegrityError:
            db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="绑定码生成失败，请重试",
    )


def update_class(
    db: Session, class_id: int, payload: JournalClassUpdate
) -> JournalClass:
    dao = JournalClassDAO(db)
    journal_class = dao.get(class_id)
    if not journal_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    values = payload.model_dump(exclude_unset=True)
    if "name" in values and values["name"] is not None:
        values["name"] = _normalize_content(str(values["name"]))
    return dao.update(journal_class, values)


def regenerate_class_binding_code(db: Session, class_id: int) -> JournalClass:
    dao = JournalClassDAO(db)
    journal_class = dao.get(class_id)
    if not journal_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="班级不存在")

    for _ in range(10):
        try:
            return dao.update(journal_class, {"binding_code": _generate_binding_code()})
        except IntegrityError:
            db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="绑定码生成失败，请重试",
    )


def get_my_binding(db: Session, current_user: User) -> JournalBindingOut:
    membership = JournalClassMembershipDAO(db).get_by_user_id(current_user.id)
    if not membership:
        return JournalBindingOut(is_bound=False, class_info=None)

    journal_class = JournalClassDAO(db).get(membership.class_id)
    if not journal_class:
        return JournalBindingOut(is_bound=False, class_info=None)
    return JournalBindingOut(
        is_bound=True,
        class_info=JournalClassOut.model_validate(journal_class),
    )


def bind_class(db: Session, *, binding_code: str, current_user: User) -> JournalBindingOut:
    normalized_code = binding_code.strip().upper()
    if not normalized_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="绑定码不能为空")

    membership_dao = JournalClassMembershipDAO(db)
    existing = membership_dao.get_by_user_id(current_user.id)
    if existing:
        journal_class = JournalClassDAO(db).get(existing.class_id)
        return JournalBindingOut(
            is_bound=True,
            class_info=(
                JournalClassOut.model_validate(journal_class)
                if journal_class
                else None
            ),
        )

    journal_class = JournalClassDAO(db).get_by_binding_code(normalized_code)
    if not journal_class or not journal_class.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="绑定码无效")

    membership_dao.create(class_id=journal_class.id, user_id=current_user.id)
    return JournalBindingOut(
        is_bound=True,
        class_info=JournalClassOut.model_validate(journal_class),
    )
