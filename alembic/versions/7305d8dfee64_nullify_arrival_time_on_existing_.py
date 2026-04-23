from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '7305d8dfee64'
down_revision = None  # ← replace with the previous migration's revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "event_parish_registrations",
        "arrival_time",
        existing_type=sa.DateTime(),
        server_default=None,
        nullable=True
    )

    op.execute(
        "UPDATE event_parish_registrations SET arrival_time = NULL"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE event_parish_registrations SET arrival_time = NOW()"
    )
    op.alter_column(
        "event_parish_registrations",
        "arrival_time",
        existing_type=sa.DateTime(),
        server_default=sa.text("now()"),
        nullable=False
    )