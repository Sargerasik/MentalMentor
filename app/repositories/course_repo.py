from __future__ import annotations
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course import Courses

async def create(db: AsyncSession, **data) -> Courses:
    obj = Courses(**data)
    db.add(obj); await db.flush()
    return obj

async def get(db: AsyncSession, course_id: int) -> Courses | None:
    res = await db.execute(select(Courses).where(Courses.id == course_id))
    return res.scalar_one_or_none()

async def get_by_id(db: AsyncSession, course_id: int) -> Optional[Courses]:
    return await db.get(Courses, course_id)

async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Courses]:
    res = await db.execute(select(Courses).where(Courses.slug == slug))
    return res.scalar_one_or_none()

async def list_public(db: AsyncSession, limit: int = 50, offset: int = 0) -> Sequence[Courses]:
    res = await db.execute(select(Courses).where(Courses.is_public == True).order_by(Courses.id.desc()).limit(limit).offset(offset))
    return res.scalars().all()
