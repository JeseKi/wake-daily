# -*- coding: utf-8 -*-
"""觉知日记服务层。"""

from __future__ import annotations

from .admin import get_admin_dashboard, list_admin_awareness_sessions
from .analysis import (
    analyze_free_content,
    build_objective_segments,
    evaluate_objectivity,
    normalize_top_analysis_marks,
)
from .awareness import (
    create_awareness_session,
    list_recent_awareness_sessions,
    update_awareness_session_inquiries,
    update_awareness_session_review,
)
from .classes import (
    bind_class,
    create_class,
    get_my_binding,
    list_classes,
    regenerate_class_binding_code,
    update_class,
)
from .constants import ENTRY_MODE_AWARENESS, ENTRY_MODE_FREE_REFLECTION
from .entries import create_entry, create_relief_feedback, list_recent_entries
from .growth import get_growth
from .questions import (
    create_daily_question,
    delete_daily_question,
    get_today_question,
    list_daily_questions,
    update_daily_question,
)
from .resonance import (
    create_resonance_feedback,
    create_resonance_item,
    delete_resonance_item,
    list_resonance_items,
)

__all__ = [
    "ENTRY_MODE_AWARENESS",
    "ENTRY_MODE_FREE_REFLECTION",
    "analyze_free_content",
    "bind_class",
    "build_objective_segments",
    "create_awareness_session",
    "create_class",
    "create_daily_question",
    "create_entry",
    "create_relief_feedback",
    "create_resonance_feedback",
    "create_resonance_item",
    "delete_daily_question",
    "delete_resonance_item",
    "evaluate_objectivity",
    "get_admin_dashboard",
    "get_growth",
    "get_my_binding",
    "get_today_question",
    "list_admin_awareness_sessions",
    "list_classes",
    "list_daily_questions",
    "list_recent_awareness_sessions",
    "list_recent_entries",
    "list_resonance_items",
    "normalize_top_analysis_marks",
    "regenerate_class_binding_code",
    "update_awareness_session_inquiries",
    "update_awareness_session_review",
    "update_class",
    "update_daily_question",
]
