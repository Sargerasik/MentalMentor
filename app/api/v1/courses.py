from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_roles
from app.db.session import get_session
from app.schemas.course import CourseCreate, CourseRead, CourseProgressRead, CourseProgressUpdate
from app.repositories import course_repo, course_progress_repo
from app.services import storage

router = APIRouter()

# --- ADMIN: подготовка загрузки PDF (опционально, можно грузить вне API) ---
@router.get("/upload_url", dependencies=[Depends(require_roles("admin"))])
async def get_upload_url(key: str):
    return {"upload_url": storage.presign_put(key)}

# --- ADMIN: регистрация курса ---
@router.post("", response_model=CourseRead, status_code=201, dependencies=[Depends(require_roles("admin"))])
async def create_course(payload: CourseCreate, db: AsyncSession = Depends(get_session)):
    exists = await course_repo.get_by_slug(db, payload.slug)
    if exists:
        raise HTTPException(status_code=409, detail="slug already exists")
    obj = await course_repo.create(db, **payload.model_dump())
    await db.commit(); await db.refresh(obj)
    return obj

# --- AUTH: список/детали курса ---
@router.get("", response_model=list[CourseRead])
async def list_courses(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_session),
                       _=Depends(get_current_user)):
    return await course_repo.list_public(db, limit=limit, offset=offset)

@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: int, db: AsyncSession = Depends(get_session), _=Depends(get_current_user)):
    obj = await course_repo.get_by_id(db, course_id)
    if not obj or not obj.is_public:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

# --- AUTH: скачать PDF (pre-signed) ---
@router.get("/{course_id}/download")
async def download_course(course_id: int, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    obj = await course_repo.get_by_id(db, course_id)
    if not obj or not obj.is_public:
        raise HTTPException(status_code=404, detail="Not found")
    url = storage.presign_get(obj.storage_key)
    return {"url": url}

# --- AUTH: старт курса / мой прогресс ---
@router.post("/{course_id}/start", response_model=CourseProgressRead, status_code=201)
async def start_course(course_id: int, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    course = await course_repo.get_by_id(db, course_id)
    if not course or not course.is_public:
        raise HTTPException(status_code=404, detail="Not found")

    cp = await course_progress_repo.get(db, current_user.id, course_id)
    if cp:
        return CourseProgressRead(course_id=course_id, status=cp.status, progress_percent=cp.progress_percent, current_page=cp.current_page)

    cp = await course_progress_repo.create(db, current_user.id, course_id, course.version)
    await db.commit(); await db.refresh(cp)
    return CourseProgressRead(course_id=course_id, status=cp.status, progress_percent=cp.progress_percent, current_page=cp.current_page)

@router.get("/{course_id}/progress", response_model=CourseProgressRead)
async def get_my_progress(course_id: int, db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    cp = await course_progress_repo.get(db, current_user.id, course_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Not started")
    return CourseProgressRead(course_id=course_id, status=cp.status, progress_percent=cp.progress_percent, current_page=cp.current_page)

@router.patch("/{course_id}/progress", response_model=CourseProgressRead)
async def update_my_progress(course_id: int, payload: CourseProgressUpdate,
                             db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    cp = await course_progress_repo.get(db, current_user.id, course_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Not started")
    cp = await course_progress_repo.update_progress(
        db, cp,
        progress_percent=payload.progress_percent,
        current_page=payload.current_page,
        status=payload.status
    )
    await db.commit(); await db.refresh(cp)
    return CourseProgressRead(course_id=course_id, status=cp.status, progress_percent=cp.progress_percent, current_page=cp.current_page)

# --- AUTH: список моих курсов c прогрессом ---
@router.get("/me/list", response_model=list[CourseProgressRead])
async def my_courses(db: AsyncSession = Depends(get_session), current_user = Depends(get_current_user)):
    rows = await course_progress_repo.list_for_user(db, current_user.id)
    return [CourseProgressRead(course_id=r.course_id, status=r.status, progress_percent=r.progress_percent, current_page=r.current_page) for r in rows]
