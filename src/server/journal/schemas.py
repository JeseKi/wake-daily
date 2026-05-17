# -*- coding: utf-8 -*-
"""觉知日记 Pydantic 模型。"""

from datetime import datetime

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

