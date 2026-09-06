"""add problem review flow

Revision ID: 20260828_0003
Revises: 20260828_0002
Create Date: 2026-08-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260828_0003"
down_revision = "20260828_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "problem_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("checklist", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_problem_reviews_problem_created", "problem_reviews", ["problem_id", "created_at"])
    op.create_index("ix_problem_reviews_reviewer_created", "problem_reviews", ["reviewer_user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_problem_reviews_reviewer_created", table_name="problem_reviews")
    op.drop_index("ix_problem_reviews_problem_created", table_name="problem_reviews")
    op.drop_table("problem_reviews")
