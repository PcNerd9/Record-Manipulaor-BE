"""add user, refresh_token, records and dataset tables

Revision ID: d8eae9dd27bc
Revises: 27d091d87620
Create Date: 2026-02-04 23:08:43.784210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8eae9dd27bc'
down_revision: Union[str, Sequence[str], None] = '27d091d87620'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
