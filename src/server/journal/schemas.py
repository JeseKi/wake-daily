# -*- coding: utf-8 -*-
"""觉知日记 Pydantic 模型。"""

from datetime import datetime
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class DailyQuestionOut(BaseModel):
    id: int
    content: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyQuestionCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0, le=999999)


class DailyQuestionUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=999999)


class JournalEntryCreate(BaseModel):
    question_id: int = Field(..., ge=1)
    content: str = Field(..., min_length=1, max_length=20000)


class AttachmentMatchOut(BaseModel):
    word: str
    start: int
    end: int


class JournalEntryOut(BaseModel):
    id: int
    user_id: int
    question_id: int
    question_content: str
    content: str
    created_at: datetime
    updated_at: datetime
    attachment_matches: list[AttachmentMatchOut]
    relief_count: int
    has_relief_feedback: bool


class ReliefFeedbackOut(BaseModel):
    entry_id: int
    relief_count: int
    has_relief_feedback: bool


class JournalClassOut(BaseModel):
    id: int
    name: str
    binding_code: str
    created_by_user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    is_active: bool = True


class JournalClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    is_active: bool | None = None


class JournalClassBind(BaseModel):
    binding_code: str = Field(..., min_length=1, max_length=32)


class JournalBindingOut(BaseModel):
    is_bound: bool
    class_info: JournalClassOut | None = None


class ObjectivityWarningOut(BaseModel):
    event_index: int
    word: str
    message: str


class AwarenessSessionCreate(BaseModel):
    objective_events: list[str] = Field(..., min_length=1, max_length=3)
    selected_event_index: int = Field(..., ge=0, le=2)
    emotion_label: str = Field(..., min_length=1, max_length=50)
    emotion_note: str = Field(..., min_length=1, max_length=2000)
    present_anchor: str = Field(..., min_length=1, max_length=2000)


class AwarenessSessionReviewUpdate(BaseModel):
    review_score: int | None = Field(default=None, ge=0, le=5)
    review_comment: str | None = Field(default=None, max_length=2000)
    reward_label: str | None = Field(default=None, max_length=120)


class AwarenessSessionOut(BaseModel):
    id: int
    user_id: int
    class_id: int
    objective_events: list[str]
    selected_event_index: int
    emotion_label: str
    emotion_note: str
    present_anchor: str
    objectivity_warnings: list[ObjectivityWarningOut]
    submitted_on: date
    review_score: int | None
    review_comment: str | None
    reward_label: str | None
    reviewed_by_user_id: int | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminAwarenessSessionOut(AwarenessSessionOut):
    student_username: str
    student_name: str | None
    class_name: str
    is_collected_to_resonance: bool


class GrowthOut(BaseModel):
    streak_days: int
    total_sessions: int
    tree_stage: str
    badges: list[str]


class ResonanceItemCreate(BaseModel):
    excerpt: str | None = Field(default=None, max_length=1000)


class ResonanceItemOut(BaseModel):
    id: int
    session_id: int
    class_id: int
    excerpt: str
    empathy_count: int
    has_empathy_feedback: bool
    created_at: datetime


class ResonanceFeedbackOut(BaseModel):
    item_id: int
    empathy_count: int
    has_empathy_feedback: bool


class AdminDashboardOut(BaseModel):
    class_count: int
    student_count: int
    submitted_today_count: int
    submission_rate: float
    total_sessions: int
    resonance_count: int
    emotion_counts: dict[str, int]
