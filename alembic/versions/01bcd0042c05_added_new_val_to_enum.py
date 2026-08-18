"""added new val to enum

Revision ID: 01bcd0042c05
Revises: cb9b6f0d9879
Create Date: 2026-08-17 23:15:07.531372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01bcd0042c05'
down_revision: Union[str, Sequence[str], None] = 'cb9b6f0d9879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("alter type book_status "
               "add value 'REMOVED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
