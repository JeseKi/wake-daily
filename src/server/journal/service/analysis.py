# -*- coding: utf-8 -*-
"""自由书写分析与客观性提示。"""

from __future__ import annotations

from typing import NamedTuple

from .constants import ANALYSIS_RULES, OBJECTIVE_SEGMENT_MESSAGE, SUBJECTIVE_WORDS
from ..schemas import AnalysisMarkOut, ObjectiveSegmentOut, ObjectivityWarningOut


class AnalysisOccurrence(NamedTuple):
    word: str
    category: str
    start: int
    end: int
    importance: int


def evaluate_objectivity(events: list[str]) -> list[ObjectivityWarningOut]:
    warnings: list[ObjectivityWarningOut] = []
    for index, event in enumerate(events):
        if "我" in event:
            warnings.append(
                ObjectivityWarningOut(
                    event_index=index,
                    word="我",
                    message="请尝试使用第三人称视角，避免使用“我”。",
                )
            )
        for word in SUBJECTIVE_WORDS:
            if word in event:
                warnings.append(
                    ObjectivityWarningOut(
                        event_index=index,
                        word=word,
                        message=f"检测到主观词“{word}”，请确认是否在描述事实。",
                    )
                )
    return warnings


def analyze_free_content(content: str) -> list[AnalysisMarkOut]:
    occurrences: list[AnalysisOccurrence] = []
    for word, category, importance in ANALYSIS_RULES:
        start = content.find(word)
        while start != -1:
            occurrences.append(
                AnalysisOccurrence(
                    word=word,
                    category=category,
                    start=start,
                    end=start + len(word),
                    importance=importance,
                )
            )
            start = content.find(word, start + len(word))

    occurrences.sort(key=lambda item: (item.start, item.word))
    top_keys: set[tuple[int, int, str]] = set()
    top_signatures: set[tuple[str, str]] = set()
    for item in sorted(occurrences, key=lambda item: (-item.importance, item.start)):
        signature = (item.word, item.category)
        if signature in top_signatures:
            continue
        top_signatures.add(signature)
        top_keys.add((item.start, item.end, item.word))
        if len(top_keys) >= 3:
            break
    return [
        AnalysisMarkOut(
            id=f"m{index}",
            word=item.word,
            category=item.category,
            start=item.start,
            end=item.end,
            importance=item.importance,
            question=_question_for_mark(item.word, item.category),
            is_top=(item.start, item.end, item.word) in top_keys,
        )
        for index, item in enumerate(occurrences, start=1)
    ]


def normalize_top_analysis_marks(
    marks: list[AnalysisMarkOut],
) -> list[AnalysisMarkOut]:
    top_ids: set[str] = set()
    top_signatures: set[tuple[str, str]] = set()
    for mark in sorted(marks, key=lambda item: (-item.importance, item.start)):
        signature = (mark.word, mark.category)
        if signature in top_signatures:
            continue
        top_signatures.add(signature)
        top_ids.add(mark.id)
        if len(top_ids) >= 3:
            break
    return [mark.model_copy(update={"is_top": mark.id in top_ids}) for mark in marks]


def build_objective_segments(
    content: str, marks: list[AnalysisMarkOut]
) -> list[ObjectiveSegmentOut]:
    if not content:
        return []
    marked_ranges = [(mark.start, mark.end) for mark in marks]
    segments: list[ObjectiveSegmentOut] = []
    cursor = 0
    for index, char in enumerate(content):
        if char not in "。！？!?；;\n":
            continue
        _append_objective_segment(content, cursor, index + 1, marked_ranges, segments)
        cursor = index + 1
    _append_objective_segment(content, cursor, len(content), marked_ranges, segments)
    return segments


def _append_objective_segment(
    content: str,
    start: int,
    end: int,
    marked_ranges: list[tuple[int, int]],
    segments: list[ObjectiveSegmentOut],
) -> None:
    raw = content[start:end]
    stripped = raw.strip()
    if not stripped:
        return
    leading_space = len(raw) - len(raw.lstrip())
    trailing_space = len(raw.rstrip())
    segment_start = start + leading_space
    segment_end = start + trailing_space
    has_mark = any(
        mark_start < segment_end and mark_end > segment_start
        for mark_start, mark_end in marked_ranges
    )
    if not has_mark:
        segments.append(
            ObjectiveSegmentOut(
                text=stripped,
                start=segment_start,
                end=segment_end,
                message=OBJECTIVE_SEGMENT_MESSAGE,
            )
        )


def _question_for_mark(word: str, category: str) -> str:
    if category == "self":
        return f"当你写下“{word}”时，你最想被看见的是什么？"
    if category == "absolute":
        return f"这个“{word}”背后，你在守护什么？"
    if category == "emotion":
        return f"这个“{word}”出现时，它在提醒你哪个需要？"
    return f"如果先放下“{word}”这个判断，你真正希望发生什么？"
