from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey, SmallInteger, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.mixins import TimestampMixin

class CourseProgress(TimestampMixin, Base):
    __tablename__ = "course_progress"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_progress_user_course"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)

    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)  # 0=in_progress, 1=paused, 2=completed
    progress_percent: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)  # 0..100
    current_page: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    course_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # на момент старта
