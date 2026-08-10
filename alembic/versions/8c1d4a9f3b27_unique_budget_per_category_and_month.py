"""unique budget per category and month

Revision ID: 8c1d4a9f3b27
Revises: 5e5ca0e50415
Create Date: 2026-08-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8c1d4a9f3b27'
down_revision: Union[str, None] = '5e5ca0e50415'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop rows that would violate the constraint, keeping the newest budget.
    op.execute("""
        DELETE FROM budgets a
        USING budgets b
        WHERE a.user_id = b.user_id
          AND a.category_id = b.category_id
          AND a.month = b.month
          AND a.created_at < b.created_at
    """)
    op.create_unique_constraint(
        'uq_budget_user_category_month', 'budgets', ['user_id', 'category_id', 'month']
    )


def downgrade() -> None:
    op.drop_constraint('uq_budget_user_category_month', 'budgets', type_='unique')
