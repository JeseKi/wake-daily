# -*- coding: utf-8 -*-
"""觉知日记初始化数据。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .models import DailyQuestion

DEFAULT_DAILY_QUESTIONS = (
    "今天有什么念头反复来找你？",
    "今天哪一刻，你发现自己又在用力证明什么？",
    "如果不用急着变好，今天你最想诚实写下什么？",
    "今天你对自己说了哪个“应该”？",
    "此刻有什么事情，其实可以先轻轻放一放？",
    "今天哪个不甘心，让你多停留了一会儿？",
    "如果把答案放慢一点，你现在最真实的感受是什么？",
)


def seed_default_daily_questions(db: Session) -> None:
    existing = db.query(DailyQuestion.id).first()
    if existing:
        return

    for index, content in enumerate(DEFAULT_DAILY_QUESTIONS, start=1):
        db.add(
            DailyQuestion(
                content=content,
                is_active=True,
                sort_order=index * 10,
            )
        )
    db.commit()

