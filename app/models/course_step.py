from __future__ import annotations
import enum
from sqlalchemy import ForeignKey, Enum, Integer, String, JSON, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.course import Courses  # класс Course уже есть

class StepType(str, enum.Enum):
    meditation = "meditation"
    reading    = "reading"
    quiz       = "quiz"
    reflection = "reflection"
    video      = "video"
    exercise   = "exercise"

class CourseStep(Base):
    __tablename__ = "course_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer)  # порядок в курсе
    title: Mapped[str] = mapped_column(String(200))
    type: Mapped[StepType] = mapped_column(Enum(StepType, name="course_step_type"))
    # JSON-конфиг параметров этапа (зависит от type)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    course: Mapped[Courses] = relationship(back_populates="steps")

    __table_args__ = (
        UniqueConstraint("course_id", "order_index", name="uq_course_step_order"),
        Index("ix_course_steps_course_order", "course_id", "order_index"),
    )