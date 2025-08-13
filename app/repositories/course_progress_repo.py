from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course_progress import CourseProgress

async def get(db: AsyncSession, user_id: int, course_id: int) -> Optional[CourseProgress]:
    res = await db.execute(select(CourseProgress).where(and_(
        CourseProgress.user_id == user_id, CourseProgress.course_id == course_id)))
    return res.scalar_one_or_none()

async def create(db: AsyncSession, user_id: int, course_id: int, course_version: int) -> CourseProgress:
    obj = CourseProgress(user_id=user_id, course_id=course_id, course_version=course_version, started_at=datetime.utcnow())
    db.add(obj); await db.flush()
    return obj

async def update_progress(db: AsyncSession, obj: CourseProgress, *, progress_percent: int, current_page: int, status: int | None):
    obj.progress_percent = progress_percent
    obj.current_page = current_page
    if status is not None:
        obj.status = status
    if progress_percent >= 100 and obj.completed_at is None:
        obj.completed_at = datetime.utcnow()
        obj.status = 2
    await db.flush()
    return obj

async def list_for_user(db: AsyncSession, user_id: int):
    res = await db.execute(select(CourseProgress).where(CourseProgress.user_id == user_id))
    return res.scalars().all()
