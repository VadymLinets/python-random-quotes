"""create quotes table

Revision ID: 33977e8b1553
Revises:
Create Date: 2024-06-26 14:07:25.458769

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "33977e8b1553"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("quote", sa.Text, nullable=False),
        sa.Column("author", sa.Text),
        sa.Column("likes", sa.Integer),
        sa.Column("tags", sa.ARRAY(sa.Text)),
    )


def downgrade() -> None:
    op.drop_table("quotes")
