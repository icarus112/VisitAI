"""migrate booking status enum

Revision ID: f4bbffaf9762
Revises: caf4472bf995
Create Date: 2026-08-13 22:32:00.690104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4bbffaf9762'
down_revision: Union[str, Sequence[str], None] = 'caf4472bf995'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TYPE book_status
        RENAME TO book_status_old
    """)

    op.execute("""
        CREATE TYPE book_status AS ENUM (
            'PENDING',
            'CONFIRMED',
            'CANCELLED',
            'COMPLETED',
            'NO_SHOW'
        )
    """)

    op.execute("""
        ALTER TABLE bookings
        ALTER COLUMN status TYPE book_status
        USING (
            CASE status::text
                WHEN 'PAID' THEN 'CONFIRMED'
                WHEN 'UNPAID' THEN 'PENDING'
                WHEN 'FAILED_PAY' THEN 'PENDING'
                ELSE status::text
            END
        )::book_status
    """)

    op.execute("""
        DROP TYPE book_status_old
    """)