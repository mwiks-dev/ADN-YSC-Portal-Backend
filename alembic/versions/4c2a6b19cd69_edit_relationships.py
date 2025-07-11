"""edit relationships

Revision ID: 4c2a6b19cd69
Revises: 2a1549377f04
Create Date: 2025-07-03 14:48:52.742800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2a6b19cd69'
down_revision: Union[str, Sequence[str], None] = '2a1549377f04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('idx_parish_id'), 'outstations', ['parish_id'], unique=False)
    # ### end Alembic commands ###
