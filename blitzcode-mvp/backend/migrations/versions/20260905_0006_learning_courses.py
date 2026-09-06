"""add learning courses

Revision ID: 20260905_0006
Revises: 20260831_0005
Create Date: 2026-09-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260905_0006"
down_revision = "20260831_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("access_type", sa.String(length=20), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_slug"), "courses", ["slug"], unique=True)
    op.create_index("ix_courses_status_access_level", "courses", ["status", "access_type", "level"])
    op.create_index("ix_courses_tags_gin", "courses", ["tags"], postgresql_using="gin")

    op.create_table(
        "course_lessons",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_preview", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "position", name="uq_course_lesson_position"),
    )
    op.create_index("ix_course_lessons_course_position", "course_lessons", ["course_id", "position"])

    op.create_table(
        "course_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "course_id", name="uq_course_enrollment_user_course"),
    )
    op.create_index("ix_course_enrollments_user_status", "course_enrollments", ["user_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_course_enrollments_user_status", table_name="course_enrollments")
    op.drop_table("course_enrollments")
    op.drop_index("ix_course_lessons_course_position", table_name="course_lessons")
    op.drop_table("course_lessons")
    op.drop_index("ix_courses_tags_gin", table_name="courses")
    op.drop_index("ix_courses_status_access_level", table_name="courses")
    op.drop_index(op.f("ix_courses_slug"), table_name="courses")
    op.drop_table("courses")
