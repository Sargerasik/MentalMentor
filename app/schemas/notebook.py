from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class MoodEnum(str, Enum):
    good = "good"
    ok   = "ok"
    bad  = "bad"

class NotebookCreate(BaseModel):
    entry_date: date = Field(default_factory=date.today)
    mood: MoodEnum
    title: Optional[str] = None
    content: Optional[str] = None

class NotebookUpdate(BaseModel):
    mood: Optional[MoodEnum] = None
    title: Optional[str] = None
    content: Optional[str] = None

class NotebookRead(BaseModel):
    id: int
    user_id: int
    entry_date: date
    mood: MoodEnum
    title: Optional[str] = None
    content: Optional[str] = None

    class Config:
        from_attributes = True
