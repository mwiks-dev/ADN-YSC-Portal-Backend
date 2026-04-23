"""add admitted_by to event parish registrations

Revision ID: c5b2587fe6c1
Revises: fef74a39bee0
Create Date: 2026-04-22 18:40:18.849380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5b2587fe6c1'
down_revision: Union[str, Sequence[str], None] = 'fef74a39bee0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "event_parish_registrations",
        sa.Column("admitted_by", sa.Integer, nullable=True),
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "event_parish_registrations",
        "admitted_by",
    )
