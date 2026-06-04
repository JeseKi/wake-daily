# -*- coding: utf-8 -*-
"""觉知日记服务常量。"""

from __future__ import annotations

import string

ENTRY_MODE_AWARENESS = "awareness_v1"
ENTRY_MODE_FREE_REFLECTION = "free_reflection_v1"

ATTACHMENT_WORDS = ("应该", "必须", "不甘心", "非要", "一定", "不能", "凭什么", "早知道")

SUBJECTIVE_WORDS = (
    "觉得",
    "想",
    "认为",
    "无聊",
    "开心",
    "难过",
    "烦躁",
    "感觉",
    "总是",
    "肯定",
    "担心",
    "害怕",
    "希望",
    "讨厌",
    "喜欢",
    "竟然",
    "不负责任",
    "莫名其妙",
)

ANALYSIS_RULES: tuple[tuple[str, str, int], ...] = (
    ("总是", "absolute", 100),
    ("肯定", "absolute", 100),
    ("一定", "absolute", 100),
    ("必须", "absolute", 100),
    ("不能", "absolute", 100),
    ("愤怒", "emotion", 95),
    ("生气", "emotion", 95),
    ("难过", "emotion", 95),
    ("烦躁", "emotion", 95),
    ("害怕", "emotion", 95),
    ("担心", "emotion", 95),
    ("讨厌", "emotion", 95),
    ("喜欢", "emotion", 90),
    ("希望", "emotion", 90),
    ("觉得", "judgment", 80),
    ("认为", "judgment", 80),
    ("不负责任", "judgment", 85),
    ("莫名其妙", "judgment", 85),
    ("我", "self", 70),
)

BINDING_CODE_LENGTH = 8
BINDING_CODE_ALPHABET = string.ascii_uppercase + string.digits
OBJECTIVE_SEGMENT_MESSAGE = "这里更接近事实观察，写得很清楚。"
