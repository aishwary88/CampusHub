"""add oauth fields

Revision ID: add_oauth_fields
Revises: dd69ffc95f16
Create Date: 2026-06-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_oauth_fields'
down_revision: Union[str, Sequence[str], None] = 'dd69ffc95f16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Alter password_hash to be nullable
    op.alter_column('users', 'password_hash',
               existing_type=sa.String(length=255),
               nullable=True)
    
    # 2. Add google_id column
    op.add_column('users', sa.Column('google_id', sa.String(length=255), nullable=True))
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])

    # 3. Add auth_provider column
    op.add_column('users', sa.Column('auth_provider', sa.String(length=20), server_default='EMAIL', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'auth_provider')
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.drop_column('users', 'google_id')
    op.alter_column('users', 'password_hash',
               existing_type=sa.String(length=255),
               nullable=False)
