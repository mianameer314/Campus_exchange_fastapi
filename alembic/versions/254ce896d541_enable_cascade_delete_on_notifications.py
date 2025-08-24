"""Enable cascade delete on notifications

Revision ID: 254ce896d541
Revises: f5e8a9b3c7d2
Create Date: 2025-08-24 14:22:47.241785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '254ce896d541'
down_revision: Union[str, Sequence[str], None] = 'f5e8a9b3c7d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(op.f('notifications_user_id_fkey'), 'notifications', type_='foreignkey')
    op.create_foreign_key(None, 'notifications', 'users', ['user_id'], ['id'], ondelete='CASCADE')

def downgrade() -> None:
    op.drop_constraint(None, 'notifications', type_='foreignkey')
    op.create_foreign_key(op.f('notifications_user_id_fkey'), 'notifications', 'users', ['user_id'], ['id'])
