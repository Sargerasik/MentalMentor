# app/api/v1/course_steps.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_roles
from app.db.session import get_session
from app.repositories import course_step_repo, course_repo, course_step_progress_repo
from app.schemas.steps import CourseStepCreate, CourseStepRead, StepCompletePayload

router = APIRouter()

# админ: создать шаг
@router.post("/courses/{course_id}/steps", response_model=CourseStepRead, dependencies=[Depends(require_roles("admin"))])
async def create_step(course_id: int, payload: CourseStepCreate, db: AsyncSession = Depends(get_session)):
    course = await course_repo.get(db, course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    # валидация соответствия type и config._type — pydantic уже сделал
    obj = await course_step_repo.create(
        db,
        course_id=course_id,
        title=payload.title,
        order_index=payload.order_index,
        type=payload.type,
        config=payload.config.model_dump(),
    )
    await db.commit()
    return obj

# пользователь: получить шаги курса
@router.get("/courses/{course_id}/steps", response_model=list[CourseStepRead])
async def list_steps(course_id: int, db: AsyncSession = Depends(get_session), user=Depends(get_current_user)):
    steps = await course_step_repo.list_by_course(db, course_id)
    return steps

# пользователь: начать шаг
@router.post("/steps/{step_id}/start", status_code=204)
async def start_step(step_id: int, db: AsyncSession = Depends(get_session), user=Depends(get_current_user)):
    # (опционально) проверить, что шаг принадлежит курсу, на который юзер записан
    await course_step_progress_repo.upsert_start(db, user.id, step_id)
    await db.commit()
    return None

# пользователь: завершить шаг с метриками
@router.post("/steps/{step_id}/complete", status_code=204)
async def complete_step(step_id: int, payload: StepCompletePayload, db: AsyncSession = Depends(get_session), user=Depends(get_current_user)):
    # валидация payload.metrics уже сделана схемой
    await course_step_progress_repo.complete(db, user.id, step_id, metrics=payload.metrics.model_dump())
    await db.commit()
    return None
