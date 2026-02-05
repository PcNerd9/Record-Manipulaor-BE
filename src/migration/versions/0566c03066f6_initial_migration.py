"""initial migration

Revision ID: 0566c03066f6
Revises: ba8a98f76c66
Create Date: 2026-02-04 23:00:14.538552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0566c03066f6'
down_revision: Union[str, Sequence[str], None] = 'ba8a98f76c66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
