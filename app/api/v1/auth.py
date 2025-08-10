from __future__ import annotations
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.deps import get_current_user
from app.core.jwt import create_token, decode_token, is_refresh
from app.core.security import hash_password, verify_password
from app.core.settings import settings
from app.db.session import get_session
from app.repositories import user_repo
from app.schemas.auth import TokenPair
from app.schemas.user import UserCreate, UserRead

router = APIRouter()

def _refresh_key(jti: str) -> str:
    return f"refresh:{jti}"

async def _store_refresh(redis: Redis, jti: str, user_id: int) -> None:
    ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    await redis.set(_refresh_key(jti), str(user_id), ex=ttl)

async def _consume_refresh(redis: Redis, jti: str) -> int | None:
    # атомарно читаем и удаляем (rotation)
    pipe = redis.pipeline()
    pipe.get(_refresh_key(jti))
    pipe.delete(_refresh_key(jti))
    val, _ = await pipe.execute()
    return int(val) if val is not None else None

@router.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_session)):
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

@router.post("/login", response_model=TokenPair)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    user = await user_repo.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access, _ = create_token(sub=str(user.id), type_="access", extra={"role": user.role.value})
    refresh, jti = create_token(sub=str(user.id), type_="refresh")

    await _store_refresh(request.app.state.redis, jti, user.id)

    return TokenPair(access_token=access, refresh_token=refresh)

# JSON-вариант логина для фронта (если не хочешь OAuth2 form)
@router.post("/login_json", response_model=TokenPair)
async def login_json(
    body: dict[str, Any],
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    email = body.get("email")
    password = body.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")
    user = await user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access, _ = create_token(sub=str(user.id), type_="access", extra={"role": user.role.value})
    refresh, jti = create_token(sub=str(user.id), type_="refresh")
    await _store_refresh(request.app.state.redis, jti, user.id)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: Request,
    body: dict[str, str],
):
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not is_refresh(payload):
        raise HTTPException(status_code=401, detail="Not a refresh token")

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise HTTPException(status_code=401, detail="Malformed token")

    # rotation: consume + issue new pair
    user_id = await _consume_refresh(request.app.state.redis, jti)
    if user_id is None or str(user_id) != str(sub):
        raise HTTPException(status_code=401, detail="Refresh token expired or already used")

    access, _ = create_token(sub=sub, type_="access")
    new_refresh, new_jti = create_token(sub=sub, type_="refresh")
    await _store_refresh(request.app.state.redis, new_jti, int(sub))

    return TokenPair(access_token=access, refresh_token=new_refresh)

@router.post("/logout", status_code=204)
async def logout(request: Request, body: dict[str, str]):
    # делаем invalidation текущего refresh (опционально; фронт может прислать его нам)
    token = body.get("refresh_token")
    if token:
        try:
            payload = decode_token(token)
            if is_refresh(payload) and payload.get("jti"):
                await request.app.state.redis.delete(_refresh_key(payload["jti"]))
        except Exception:
            pass
    return  # 204
