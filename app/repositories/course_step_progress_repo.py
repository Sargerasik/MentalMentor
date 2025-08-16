# app/repositories/course_step_progress_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.course_step_progress import CourseStepProgress, StepStatus

async def get(db: AsyncSession, user_id: int, step_id: int) -> CourseStepProgress | None:
    q = select(CourseStepProgress).where(
        CourseStepProgress.user_id == user_id,
        CourseStepProgress.step_id == step_id
    )
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def upsert_start(db: AsyncSession, user_id: int, step_id: int) -> CourseStepProgress:
    row = await get(db, user_id, step_id)
    now = datetime.now(timezone.utc)
    if not row:
        row = CourseStepProgress(user_id=user_id, step_id=step_id, status=StepStatus.in_progress, started_at=now, metrics={})
        db.add(row)
    else:
        if row.status == StepStatus.not_started:
            row.status = StepStatus.in_progress
            row.started_at = now
    await db.flush()
    return row

async def complete(db: AsyncSession, user_id: int, step_id: int, metrics: dict) -> CourseStepProgress:
    row = await get(db, user_id, step_id)
    now = datetime.now(timezone.utc)
    if not row:
        row = CourseStepProgress(user_id=user_id, step_id=step_id, status=StepStatus.completed, started_at=now, completed_at=now, metrics=metrics)
        db.add(row)
    else:
        row.status = StepStatus.completed
        if not row.started_at:
            row.started_at = now
        row.completed_at = now
        row.metrics = metrics
    await db.flush()
    return row
    