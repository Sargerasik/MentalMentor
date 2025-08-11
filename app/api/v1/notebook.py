from __future__ import annotations
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_session
from app.schemas.notebook import NotebookCreate, NotebookUpdate, NotebookRead
from app.repositories import notebook_repo
from app.models.user import User  # тип для current_user

router = APIRouter()

def _ensure_self_or_admin(current_user: User, target_user_id: int) -> None:
    role = getattr(current_user.role, "value", current_user.role)
    if role == "admin":
        return
    if current_user.id != target_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("", response_model=List[NotebookRead])
async def list_entries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    user_id: Optional[int] = Query(None, description="admin only: user id to view"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    target_user_id = user_id or current_user.id
    _ensure_self_or_admin(current_user, target_user_id)
    items = await notebook_repo.list_for_user(db, target_user_id, limit=limit, offset=offset,
                                              date_from=date_from, date_to=date_to)
    return items

@router.get("/{entry_id}", response_model=NotebookRead)
async def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    entry = await notebook_repo.get(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    _ensure_self_or_admin(current_user, entry.user_id)
    return entry

@router.post("", response_model=NotebookRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # одна запись в день — возвращаем 409, если уже есть
    existing = await notebook_repo.get_by_date(db, current_user.id, payload.entry_date)
    if existing:
        raise HTTPException(status_code=409, detail="Entry for this date already exists")
    entry = await notebook_repo.create(
        db,
        user_id=current_user.id,
        entry_date=payload.entry_date,
        mood=payload.mood,
        title=payload.title,
        content=payload.content,
    )
    await db.commit(); await db.refresh(entry)
    return entry

@router.patch("/{entry_id}", response_model=NotebookRead)
async def update_entry(
    entry_id: int, payload: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    entry = await notebook_repo.get(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    _ensure_self_or_admin(current_user, entry.user_id)
    entry = await notebook_repo.update(
        db, entry, mood=payload.mood, title=payload.title, content=payload.content
    )
    await db.commit(); await db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    entry = await notebook_repo.get(db, entry_id)
    if not entry:
        return  # идемпотентно
    _ensure_self_or_admin(current_user, entry.user_id)
    await notebook_repo.delete(db, entry)
    await db.commit()
    return
