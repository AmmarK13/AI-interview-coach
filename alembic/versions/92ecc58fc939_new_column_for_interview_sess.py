"""New column for interview sess

Revision ID: 92ecc58fc939
Revises: 0bfb82cae5fc
Create Date: 2026-06-25 14:53:10.241009

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "92ecc58fc939"
down_revision: Union[str, Sequence[str], None] = "0bfb82cae5fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


status_enum = sa.Enum(
    "complete",
    "inprogress",
    name="status"
)


def upgrade() -> None:
    """Upgrade schema."""

    # Create PostgreSQL enum type
    status_enum.create(op.get_bind(), checkfirst=True)

    # Add column
    op.add_column(
        "interview_sessions",
        sa.Column(
            "status",
            status_enum,
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("interview_sessions", "status")

    # Drop PostgreSQL enum type
    status_enum.drop(op.get_bind(), checkfirst=True)