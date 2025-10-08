"""add created_at and updated_at to users

Revision ID: 83a3e6b10940
Revises: e9e5a28a46a9
Create Date: 2025-09-30 11:12:58.560308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83a3e6b10940'
down_revision: Union[str, Sequence[str], None] = 'e9e5a28a46a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")