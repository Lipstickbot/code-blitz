"""add course lesson content

Revision ID: 20260905_0009
Revises: 20260905_0008
Create Date: 2026-09-05
"""

from alembic import op
import sqlalchemy as sa


revision = "20260905_0009"
down_revision = "20260905_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("course_lessons", sa.Column("content", sa.Text(), nullable=False, server_default=""))
    op.add_column("course_lessons", sa.Column("checklist", sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    op.drop_column("course_lessons", "checklist")
    op.drop_column("course_lessons", "content")
