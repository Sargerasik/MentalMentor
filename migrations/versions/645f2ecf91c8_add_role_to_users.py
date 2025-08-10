"""add role to users

Revision ID: 645f2ecf91c8
Revises: 1526ad44e578
Create Date: 2025-08-10 14:06:43.224512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '645f2ecf91c8'
down_revision: Union[str, None] = '1526ad44e578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # 1) Создаём ENUM type, если его ещё нет
    role_enum = sa.Enum("user", "admin", name="role_enum")
    role_enum.create(op.get_bind(), checkfirst=True)

    # 2) Добавляем колонку, ссылаясь на уже созданный тип
    op.add_column(
        "users",
        sa.Column("role", role_enum, server_default="user", nullable=False),
    )

    # (опционально) убрать server_default после бэкапа/миграции данных
    # op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    # Удаляем колонку
    op.drop_column("users", "role")
    # И сам ENUM, если больше нигде не используется
    sa.Enum(name="role_enum").drop(op.get_bind(), checkfirst=True)
