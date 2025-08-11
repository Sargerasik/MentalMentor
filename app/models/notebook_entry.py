from __future__ import annotations
from datetime import date
import enum
from sqlalchemy import String, Text, Enum as SAEnum, UniqueConstraint, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.mixins import TimestampMixin

class MoodEnum(str, enum.Enum):
    good = "good"
    ok   = "ok"
    bad  = "bad"

class NotebookEntry(TimestampMixin, Base):
    __tablename__ = "notebook_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "entry_date", name="uq_notebook_user_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    entry_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)  # одна запись в день
    mood: Mapped[MoodEnum] = mapped_column(SAEnum(MoodEnum, name="mood_enum"), nullable=False)

    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
