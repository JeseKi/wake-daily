# -*- coding: utf-8 -*-
"""觉知日记 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter

from .admin import router as admin_router
from .student import router as student_router

router = APIRouter()
router.include_router(student_router)
router.include_router(admin_router)

__all__ = ["router"]
