from __future__ import annotations
from datetime import datetime
from app.models.mixins import TimestampMixin
from sqlalchemy import BigInteger, ForeignKey, DateTime, func, UniqueConstraint, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), index=True, nullable=False)  # 👈 меняем имя таблицы
    status: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )