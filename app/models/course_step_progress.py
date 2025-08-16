# app/models/course_step_progress.py
from __future__ import annotations
import enum
from sqlalchemy import ForeignKey, Enum, Integer, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base

class StepStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed   = "completed"

class CourseStepProgress(Base):
    __tablename__ = "course_step_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    step_id: Mapped[int] = mapped_column(ForeignKey("course_steps.id", ondelete="CASCADE"), index=True, nullable=False)

    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus, name="course_step_status"), default=StepStatus.not_started)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # метрики выполнения (зависят от типа шага): фактическое время, ответы, счёт, заметки, и т.п.
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)

    step = relationship("CourseStep")
    __table_args__ = (
        UniqueConstraint("user_id", "step_id", name="uq_user_step"),
    )
