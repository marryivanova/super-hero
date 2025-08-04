"""create tables heros

Revision ID: 6f74f3ff68cd
Revises:
Create Date: 2025-08-04 15:07:44.350110

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f74f3ff68cd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "heroes",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("intelligence", sa.Float),
        sa.Column("strength", sa.Float),
        sa.Column("speed", sa.Float),
        sa.Column("power", sa.Float),
        sa.Column("full_name", sa.String),
        sa.Column("publisher", sa.String),
        sa.Column("alignment", sa.String),
        sa.Column("image_url", sa.String),
    )


def downgrade() -> None:
    op.drop_table("heroes")
