"""Add community goals status

Revision ID: 1becfd037193
Revises:
Create Date: 2021-05-30 20:07:08.722225

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1becfd037193"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "community_goal_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_update", sa.DateTime(), nullable=False),
        sa.Column("is_finished", sa.Boolean(), nullable=False),
        sa.Column("current_tier", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("community_goal_status")
