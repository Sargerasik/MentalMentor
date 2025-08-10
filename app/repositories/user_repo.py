from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)

async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()

async def create(
    db: AsyncSession,
    *,
    email: str,
    password_hash: str,
    city: Optional[str],
    country: Optional[str],
    phone: Optional[str],
    gender: Optional[str],
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        city=city,
        country=country,
        phone=phone,
        gender=gender,  # enum маппится по строковому значению
    )
    db.add(user)
    await db.flush()  # получим id без коммита
    return user

async def update_partial(
    db: AsyncSession,
    user: User,
    *,
    city: Optional[str],
    country: Optional[str],
    phone: Optional[str],
    gender: Optional[str],
) -> User:
    if city is not None:
        user.city = city
    if country is not None:
        user.country = country
    if phone is not None:
        user.phone = phone
    if gender is not None:
        user.gender = gender
    await db.flush()
    return user
