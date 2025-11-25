"""Fix payments PK autoincrement

Revision ID: a29727fa2fd4
Revises: aff162b03735
Create Date: 2025-11-25 18:13:44.020627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a29727fa2fd4'
down_revision: Union[str, Sequence[str], None] = 'aff162b03735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
