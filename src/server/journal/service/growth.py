# -*- coding: utf-8 -*-
"""成长统计服务。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.server.auth.models import User

from ..dao import JournalAwarenessSessionDAO
from ..models import JournalAwarenessSession
from ..schemas import GrowthOut


def get_growth(db: Session, *, current_user: User) -> GrowthOut:
    sessions = JournalAwarenessSessionDAO(db).list_all_for_growth(user_id=current_user.id)
    submitted_dates = sorted({item.submitted_on for item in sessions}, reverse=True)
    streak = _calculate_streak(submitted_dates, datetime.now(timezone.utc).date())
    max_streak = _calculate_max_streak(submitted_dates)
    total = len(submitted_dates)
    return GrowthOut(
        streak_days=streak,
        max_streak_days=max_streak,
        unlocked_guided_audio_days=_unlocked_guided_audio_days(max_streak),
        total_sessions=total,
        tree_stage=_tree_stage_for_streak(streak),
        badges=_badges_for_sessions(sessions, streak),
    )


def _calculate_streak(submitted_dates: list[date], today: date) -> int:
    if not submitted_dates:
        return 0
    date_set = set(submitted_dates)
    cursor = today
    if cursor not in date_set:
        cursor = today - timedelta(days=1)
    streak = 0
    while cursor in date_set:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def _calculate_max_streak(submitted_dates: list[date]) -> int:
    if not submitted_dates:
        return 0
    ordered_dates = sorted(set(submitted_dates))
    max_streak = 1
    streak = 1
    previous = ordered_dates[0]
    for submitted_on in ordered_dates[1:]:
        if submitted_on == previous + timedelta(days=1):
            streak += 1
        else:
            streak = 1
        max_streak = max(max_streak, streak)
        previous = submitted_on
    return max_streak


def _unlocked_guided_audio_days(max_streak: int) -> int:
    if max_streak > 6:
        return 7
    return max(1, min(7, max_streak + 1))


def _tree_stage_for_streak(streak: int) -> str:
    if streak >= 14:
        return "开花"
    if streak >= 7:
        return "大树"
    if streak >= 3:
        return "小树"
    if streak >= 1:
        return "幼苗"
    return "种子"


def _badges_for_sessions(
    sessions: list[JournalAwarenessSession], streak: int
) -> list[str]:
    badges: list[str] = []
    if sessions:
        badges.append("首次完成三关觉察")
    if streak >= 3:
        badges.append("连续三天照见")
    if streak >= 7:
        badges.append("一周安静生长")
    emotion_counts: dict[str, int] = {}
    for session in sessions:
        emotion_counts[session.emotion_label] = emotion_counts.get(
            session.emotion_label, 0
        ) + 1
    if any(count >= 2 for count in emotion_counts.values()):
        badges.append("首次精准标记重复情绪")
    return badges
