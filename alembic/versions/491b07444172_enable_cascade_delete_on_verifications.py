"""Enable cascade delete on verifications

Revision ID: 491b07444172
Revises: 254ce896d541
Create Date: 2025-08-24 14:34:32.019273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '491b07444172'
down_revision: Union[str, Sequence[str], None] = '254ce896d541'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old foreign key
    op.drop_constraint("verifications_user_id_fkey", "verifications", type_="foreignkey")
    # Add new FK with cascade
    op.create_foreign_key(
        "verifications_user_id_fkey",
        "verifications",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )

def downgrade() -> None:
    # Drop cascade FK
    op.drop_constraint("verifications_user_id_fkey", "verifications", type_="foreignkey")
    # Recreate without cascade
    op.create_foreign_key(
        "verifications_user_id_fkey",
        "verifications",
        "users",
        ["user_id"],
        ["id"]
    )