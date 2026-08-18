"""change value of enum book_status

Revision ID: caf4472bf995
Revises: 92a6298b5cef
Create Date: 2026-08-13 22:18:32.233384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'caf4472bf995'
down_revision: Union[str, Sequence[str], None] = '92a6298b5cef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    def upgrade() -> None:
        # Старый enum пока оставляем вместе со всеми данными
        op.execute("""
                ALTER TYPE book_status
                RENAME TO book_status_old
            """)

        # Создаём новый enum ровно как в Python-модели
        op.execute("""
                CREATE TYPE book_status AS ENUM (
                    'PENDING',
                    'CONFIRMED',
                    'CANCELLED',
                    'COMPLETED',
                    'NO_SHOW'
                )
            """)

        # Переводим колонку со старого enum на новый
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

        # Теперь старый enum никем не используется
        op.execute("""
                DROP TYPE book_status_old
            """)


def downgrade() -> None:
    """Downgrade schema."""
