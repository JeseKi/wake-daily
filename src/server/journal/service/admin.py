# -*- coding: utf-8 -*-
"""教师端与管理统计服务。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..dao import (
    JournalAwarenessSessionDAO,
    JournalClassDAO,
    JournalClassMembershipDAO,
    JournalResonanceItemDAO,
)
from ..schemas import AdminAwarenessSessionOut, AdminDashboardOut
from .serializers import _build_admin_awareness_session_out


def list_admin_awareness_sessions(
    db: Session, *, class_id: int | None = None
) -> list[AdminAwarenessSessionOut]:
    rows = JournalAwarenessSessionDAO(db).list_admin(class_id=class_id)
    resonance_dao = JournalResonanceItemDAO(db)
    items = []
    for session, student, journal_class in rows:
        resonance_item = resonance_dao.get_by_session_id(session.id, active_only=True)
        items.append(
            _build_admin_awareness_session_out(
                session,
                student=student,
                journal_class=journal_class,
                resonance_item_id=resonance_item.id if resonance_item else None,
            )
        )
    return items


def get_admin_dashboard(db: Session) -> AdminDashboardOut:
    class_count = len(JournalClassDAO(db).list(include_inactive=True))
    student_count = JournalClassMembershipDAO(db).count_students()
    session_dao = JournalAwarenessSessionDAO(db)
    submitted_today_count = session_dao.count_submitted_on(
        datetime.now(timezone.utc).date()
    )
    submission_rate = (
        round(submitted_today_count / student_count, 4) if student_count else 0.0
    )
    return AdminDashboardOut(
        class_count=class_count,
        student_count=student_count,
        submitted_today_count=submitted_today_count,
        submission_rate=submission_rate,
        total_sessions=session_dao.count_total(),
        resonance_count=JournalResonanceItemDAO(db).count_active(),
        emotion_counts=session_dao.emotion_counts(),
    )
