from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.repositories import user_repo
from app.api.deps import get_current_user

router = APIRouter()

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_session)):
    exists = await user_repo.get_by_email(db, payload.email)
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = await user_repo.create(
        db,
        email=payload.email,
        password_hash=hash_password(payload.password),
        city=payload.city,
        country=payload.country,
        phone=payload.phone,
        gender=payload.gender.value if payload.gender else None,
    )
    await db.commit()
    await db.refresh(user)
    return user

def _ensure_self_or_admin(current_user, target_user_id: int):
    if getattr(current_user.role, "value", None) == "admin":
        return
    if current_user.id != target_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("", response_model=UserRead)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    user = await user_repo.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    _ensure_self_or_admin(current_user, user.id)
    return user

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    _ensure_self_or_admin(current_user, user_id)
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    _ensure_self_or_admin(current_user, user_id)

    user = await user_repo.update_partial(
        db,
        user,
        city=payload.city,
        country=payload.country,
        phone=payload.phone,
        gender=payload.gender.value if payload.gender else None,
    )
    await db.commit()
    await db.refresh(user)
    return user
