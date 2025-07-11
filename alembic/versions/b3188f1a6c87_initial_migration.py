"""Initial migration

Revision ID: b3188f1a6c87
Revises: 
Create Date: 2025-07-02 15:21:14.752715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3188f1a6c87'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deaneries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deaneries_id'), 'deaneries', ['id'], unique=False)
    op.create_index(op.f('ix_deaneries_name'), 'deaneries', ['name'], unique=True)
    op.create_table('parishes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('deanery_id', sa.Integer(), nullable=True),
    sa.Column('deanery_name', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['deanery_id'], ['deaneries.id'], ),
    sa.ForeignKeyConstraint(['deanery_name'], ['deaneries.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parishes_id'), 'parishes', ['id'], unique=False)
    op.create_index(op.f('ix_parishes_name'), 'parishes', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phonenumber', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('role', sa.Enum('parish_member', 'parish_moderator', 'deanery_moderator', 'ysc_coordinator', 'ysc_chaplain', name='userrole'), nullable=True),
    sa.Column('parish_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parish_id'], ['parishes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_parishes_name'), table_name='parishes')
    op.drop_index(op.f('ix_parishes_id'), table_name='parishes')
    op.drop_table('parishes')
    op.drop_index(op.f('ix_deaneries_name'), table_name='deaneries')
    op.drop_index(op.f('ix_deaneries_id'), table_name='deaneries')
    op.drop_table('deaneries')
    # ### end Alembic commands ###
