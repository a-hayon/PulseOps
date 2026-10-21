"""create services table

Revision ID: 940665df5b17
Revises: 
Create Date: 2026-10-21 12:35:35.703932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '940665df5b17'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("check_interval", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("check_interval > 0", name="ck_services_positive_interval"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("services")
