"""removed role in user model

Revision ID: 7c328fe6b82a
Revises: 83f18d581c69
Create Date: 2026-06-23 10:58:48.138546

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7c328fe6b82a'
down_revision = '83f18d581c69'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
