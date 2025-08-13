from __future__ import annotations
from sqlalchemy import String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.mixins import TimestampMixin

class Courses(TimestampMixin, Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # PDF-хранение
    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)  # e.g. "courses/intro_v1.pdf"
    pdf_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # версии/видимость
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
