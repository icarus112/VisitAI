"""added enum for admin role

Revision ID: 9606097c71d9
Revises: 01bcd0042c05
Create Date: 2026-08-19 00:31:31.709617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9606097c71d9'
down_revision: Union[str, Sequence[str], None] = '01bcd0042c05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    create type admin_role as enum (
        'SUPER_ADMIN',
        'ADMIN'
    )
    """)

    op.execute("""
    alter table admins
    alter column role type admin_role
    using role::text::admin_role
    """)


def downgrade() -> None:
    op.execute("""
    alter table admins
    alter column role type varchar
    using role::text
    """)

    op.execute("""
    drop type admin_role
    """)
