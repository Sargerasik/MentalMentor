from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class CourseCreate(BaseModel):
    slug: str
    title: str
    summary: str
    storage_key: str  # ключ в хранилище (после заливки)
    pdf_pages: Optional[int] = None
    version: int = 1
    is_public: bool = True

class CourseRead(BaseModel):
    id: int
    slug: str
    title: str
    summary: str
    storage_key: str
    pdf_pages: Optional[int] = None
    version: int
    is_public: bool

    class Config:
        from_attributes = True

class CourseProgressRead(BaseModel):
    course_id: int
    status: int
    progress_percent: int
    current_page: int

class CourseProgressUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    current_page: int = Field(ge=0)
    status: Optional[int] = None  # 0/1/2
