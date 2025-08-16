"""add course_progress fix

Revision ID: 003586e204cb
Revises: a4f5997bac90
Create Date: 2025-08-16 16:32:39.716901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003586e204cb'
down_revision: Union[str, None] = 'a4f5997bac90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "course_progress",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("course_id", sa.Integer, sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),

        sa.Column("status", sa.SmallInteger, nullable=False, server_default="0"),         # 0=in_progress,1=paused,2=completed
        sa.Column("progress_percent", sa.SmallInteger, nullable=False, server_default="0"),# 0..100
        sa.Column("current_page", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("course_version", sa.Integer, nullable=False, server_default="1"),

        # из TimestampMixin, если он у тебя добавляет столбцы — создай их тоже
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_unique_constraint("uq_progress_user_course", "course_progress", ["user_id", "course_id"])
    op.create_index("ix_course_progress_user", "course_progress", ["user_id"])
    op.create_index("ix_course_progress_course", "course_progress", ["course_id"])

    # (опционально, но полезно) ограничения целостности
    op.create_check_constraint("ck_course_progress_percent", "course_progress", "progress_percent BETWEEN 0 AND 100")
    op.create_check_constraint("ck_course_progress_status", "course_progress", "status IN (0,1,2)")

def downgrade():
    op.drop_constraint("ck_course_progress_status", "course_progress", type_="check")
    op.drop_constraint("ck_course_progress_percent", "course_progress", type_="check")
    op.drop_index("ix_course_progress_course", table_name="course_progress")
    op.drop_index("ix_course_progress_user", table_name="course_progress")
    op.drop_constraint("uq_progress_user_course", "course_progress", type_="unique")
    op.drop_table("course_progress")