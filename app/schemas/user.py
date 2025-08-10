from __future__ import annotations
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"

class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    email: EmailStr
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[constr(strip_whitespace=True, min_length=5, max_length=20)] = None
    gender: Optional[GenderEnum] = None

# Базовая «читаемая» модель
class UserRead(BaseModel):
    id: int
    email: EmailStr
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[GenderEnum] = None

    class Config:
        from_attributes = True

# Вход на создание
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[0-9\s\-()]{7,20}$",  # мягкая проверка, без строгой E.164
    )
    gender: Optional[GenderEnum] = None

# Частичное обновление
class UserUpdate(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[0-9\s\-()]{7,20}$",
    )
    gender: Optional[GenderEnum] = None