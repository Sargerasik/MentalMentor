# app/repositories/course_step_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.course_step import CourseStep

async def list_by_course(db: AsyncSession, course_id: int) -> list[CourseStep]:
    res = await db.execute(select(CourseStep).where(CourseStep.course_id == course_id).order_by(CourseStep.order_index))
    return list(res.scalars())

async def create(db: AsyncSession, *, course_id: int, title: str, order_index: int, type: str, config: dict) -> CourseStep:
    obj = CourseStep(course_id=course_id, title=title, order_index=order_index, type=type, config=config)
    db.add(obj)
    await db.flush()
    return obj
