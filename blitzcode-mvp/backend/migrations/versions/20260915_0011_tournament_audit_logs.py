"""Add tournament audit logs.

Revision ID: 20260915_0011
Revises: 20260913_0010
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260915_0011"
down_revision = "20260913_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tournament_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("action", sa.String(length=60), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tournament_audit_tournament_created",
        "tournament_audit_logs",
        ["tournament_id", "created_at"],
    )
    op.create_index(
        "ix_tournament_audit_actor_created",
        "tournament_audit_logs",
        ["actor_user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_tournament_audit_actor_created", table_name="tournament_audit_logs")
    op.drop_index("ix_tournament_audit_tournament_created", table_name="tournament_audit_logs")
    op.drop_table("tournament_audit_logs")
