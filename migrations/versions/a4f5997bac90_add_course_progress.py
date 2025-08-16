"""add course_progress

Revision ID: a4f5997bac90
Revises: d90e06404843
Create Date: 2025-08-16 16:26:05.325381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4f5997bac90'
down_revision: Union[str, None] = 'd90e06404843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
