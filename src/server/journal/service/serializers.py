# -*- coding: utf-8 -*-
"""服务层输出模型组装。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import JournalResonanceFeedbackDAO
from ..models import JournalAwarenessSession, JournalClass
from ..schemas import (
    AdminAwarenessSessionOut,
    AnalysisMarkOut,
    AwarenessSessionOut,
    InquiryRecordOut,
    ObjectivityWarningOut,
    ResonanceItemOut,
)
from .analysis import build_objective_segments, normalize_top_analysis_marks
from .constants import ENTRY_MODE_FREE_REFLECTION
from .utils import _json_loads_list


def _build_awareness_session_out(
    session: JournalAwarenessSession,
) -> AwarenessSessionOut:
    warnings = _json_loads_list(session.objectivity_warnings_json)
    analysis_marks = [
        AnalysisMarkOut.model_validate(item)
        for item in _json_loads_list(session.analysis_marks_json)
        if isinstance(item, dict)
    ]
    analysis_marks = normalize_top_analysis_marks(analysis_marks)
    inquiry_records = [
        InquiryRecordOut.model_validate(item)
        for item in _json_loads_list(session.inquiry_records_json)
        if isinstance(item, dict)
    ]
    free_content = session.free_content
    if session.entry_mode == ENTRY_MODE_FREE_REFLECTION and free_content is None:
        events = _json_loads_list(session.objective_events_json)
        free_content = str(events[0]) if events else None
    return AwarenessSessionOut(
        id=session.id,
        user_id=session.user_id,
        class_id=session.class_id,
        entry_mode=session.entry_mode,
        free_content=free_content,
        objective_events=[
            str(item) for item in _json_loads_list(session.objective_events_json)
        ],
        selected_event_index=session.selected_event_index,
        emotion_label=session.emotion_label,
        emotion_note=session.emotion_note,
        present_anchor=session.present_anchor,
        objectivity_warnings=[
            ObjectivityWarningOut.model_validate(item)
            for item in warnings
            if isinstance(item, dict)
        ],
        analysis_marks=analysis_marks,
        inquiry_records=inquiry_records,
        objective_segments=build_objective_segments(free_content or "", analysis_marks),
        submitted_on=session.submitted_on,
        review_score=session.review_score,
        review_comment=session.review_comment,
        reward_label=session.reward_label,
        reviewed_by_user_id=session.reviewed_by_user_id,
        reviewed_at=session.reviewed_at,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _build_admin_awareness_session_out(
    session: JournalAwarenessSession,
    *,
    student: User,
    journal_class: JournalClass,
    resonance_item_id: int | None,
) -> AdminAwarenessSessionOut:
    base = _build_awareness_session_out(session).model_dump()
    return AdminAwarenessSessionOut(
        **base,
        student_username=student.username,
        student_name=student.name,
        class_name=journal_class.name,
        is_collected_to_resonance=resonance_item_id is not None,
        resonance_item_id=resonance_item_id,
    )


def _build_resonance_item_out(
    db: Session,
    item,
    *,
    current_user_id: int,
) -> ResonanceItemOut:
    feedback_dao = JournalResonanceFeedbackDAO(db)
    has_feedback = item.id in feedback_dao.has_feedback_by_item_ids(
        user_id=current_user_id,
        item_ids=[item.id],
    )
    return ResonanceItemOut(
        id=item.id,
        session_id=item.session_id,
        class_id=item.class_id,
        excerpt=item.excerpt,
        empathy_count=feedback_dao.count_for_item(item.id),
        has_empathy_feedback=has_feedback,
        created_at=item.created_at,
    )
