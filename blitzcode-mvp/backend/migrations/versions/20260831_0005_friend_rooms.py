"""add friend rooms

Revision ID: 20260831_0005
Revises: 20260831_0004
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260831_0005"
down_revision = "20260831_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "friend_rooms",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("creator_user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("invited_user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["creator_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["invited_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", name="uq_friend_room_match"),
    )
    op.create_index(
        "ix_friend_rooms_invited_status_created",
        "friend_rooms",
        ["invited_user_id", "status", "created_at"],
    )
    op.create_index(
        "ix_friend_rooms_creator_status_created",
        "friend_rooms",
        ["creator_user_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_friend_rooms_creator_status_created", table_name="friend_rooms")
    op.drop_index("ix_friend_rooms_invited_status_created", table_name="friend_rooms")
    op.drop_table("friend_rooms")
