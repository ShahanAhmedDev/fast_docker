"""New Migration 2

Revision ID: 95c9df0ab2a2
Revises: 4bdb9ce7a82e
Create Date: 2023-12-16 21:15:59.127079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95c9df0ab2a2'
down_revision: Union[str, None] = '4bdb9ce7a82e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###