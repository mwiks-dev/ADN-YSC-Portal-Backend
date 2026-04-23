"""merge_heads

Revision ID: 7db95a5200a8
Revises: 7305d8dfee64, c5b2587fe6c1
Create Date: 2026-04-23 16:30:57.287273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7db95a5200a8'
down_revision: Union[str, Sequence[str], None] = ('7305d8dfee64', 'c5b2587fe6c1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
