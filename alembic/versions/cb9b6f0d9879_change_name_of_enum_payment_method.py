"""change name of enum payment_method

Revision ID: cb9b6f0d9879
Revises: f4bbffaf9762
Create Date: 2026-08-15 17:39:03.574497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb9b6f0d9879'
down_revision: Union[str, Sequence[str], None] = 'f4bbffaf9762'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("alter type paymentmethod rename to payment_method")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("alter type payment_method rename to paymentmethod")

