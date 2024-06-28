"""create views table

Revision ID: d362a4be2327
Revises: 33977e8b1553
Create Date: 2024-06-26 14:10:13.601778

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d362a4be2327"
down_revision: Union[str, None] = "33977e8b1553"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "views",
        sa.Column("user_id", sa.Text, primary_key=True),
        sa.Column("quote_id", sa.Text, primary_key=True),
        sa.Column("liked", sa.Boolean),
        sa.ForeignKeyConstraint(
            ("quote_id",),
            [
                "quotes.id",
            ],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("views")
