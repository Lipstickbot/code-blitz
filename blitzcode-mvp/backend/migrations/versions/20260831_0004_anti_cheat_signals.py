"""add anti cheat signals

Revision ID: 20260831_0004
Revises: 20260828_0003
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260831_0004"
down_revision = "20260828_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "anti_cheat_signals",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("signal_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("reviewed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anti_cheat_signals_user_created", "anti_cheat_signals", ["user_id", "created_at"])
    op.create_index("ix_anti_cheat_signals_match_created", "anti_cheat_signals", ["match_id", "created_at"])
    op.create_index("ix_anti_cheat_signals_type_reviewed", "anti_cheat_signals", ["signal_type", "reviewed"])


def downgrade() -> None:
    op.drop_index("ix_anti_cheat_signals_type_reviewed", table_name="anti_cheat_signals")
    op.drop_index("ix_anti_cheat_signals_match_created", table_name="anti_cheat_signals")
    op.drop_index("ix_anti_cheat_signals_user_created", table_name="anti_cheat_signals")
    op.drop_table("anti_cheat_signals")
