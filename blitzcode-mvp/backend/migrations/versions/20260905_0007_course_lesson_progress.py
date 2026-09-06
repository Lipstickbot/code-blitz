"""add course lesson progress

Revision ID: 20260905_0007
Revises: 20260905_0006
Create Date: 2026-09-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260905_0007"
down_revision = "20260905_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_lesson_progress",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("completed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["course_lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_course_lesson_progress_user_lesson"),
    )
    op.create_index(
        "ix_course_lesson_progress_user_course",
        "course_lesson_progress",
        ["user_id", "course_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_course_lesson_progress_user_course", table_name="course_lesson_progress")
    op.drop_table("course_lesson_progress")
