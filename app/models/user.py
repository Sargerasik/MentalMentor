from __future__ import annotations
from sqlalchemy import BigInteger, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum
from app.models.mixins import TimestampMixin
from datetime import datetime
from sqlalchemy import String, Enum as SAEnum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(TimestampMixin,Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    locale: Mapped[str] = mapped_column(String(10), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(SAEnum(GenderEnum, name="gender_enum"), nullable=True)
    role: Mapped[RoleEnum] = mapped_column(
        SAEnum(RoleEnum, name="role_enum"),
        nullable=False,
        default=RoleEnum.user,
        server_default=RoleEnum.user.value,  # чтобы дефолт ставился на уровне БД
    )