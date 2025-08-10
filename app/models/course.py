from __future__ import annotations
from datetime import datetime
from app.models.mixins import TimestampMixin
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)