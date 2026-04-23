"""add fine_amount to event parish registrations

Revision ID: fef74a39bee0
Revises: bb4302950557
Create Date: 2026-04-22 16:19:01.638165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fef74a39bee0'
down_revision: Union[str, Sequence[str], None] = 'bb4302950557'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(  
        "event_parish_registrations",
        sa.Column("fine_amount", sa.Float, nullable=False, default=0.0),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("event_parish_registrations", "fine_amount")
