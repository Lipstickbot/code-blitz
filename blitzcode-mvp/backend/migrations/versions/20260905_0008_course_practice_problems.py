"""add course practice problems

Revision ID: 20260905_0008
Revises: 20260905_0007
Create Date: 2026-09-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260905_0008"
down_revision = "20260905_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_practice_problems",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "problem_id", name="uq_course_practice_problem"),
        sa.UniqueConstraint("course_id", "position", name="uq_course_practice_position"),
    )
    op.create_index(
        "ix_course_practice_problems_course_position",
        "course_practice_problems",
        ["course_id", "position"],
    )


def downgrade() -> None:
    op.drop_index("ix_course_practice_problems_course_position", table_name="course_practice_problems")
    op.drop_table("course_practice_problems")
