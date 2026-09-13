"""Add tournament brackets.

Revision ID: 20260913_0010
Revises: 20260905_0009
Create Date: 2026-09-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260913_0010"
down_revision = "20260905_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tournaments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("creator_user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("max_players", sa.Integer(), nullable=False),
        sa.Column("player_count", sa.Integer(), nullable=False),
        sa.Column("champion_user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["champion_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["creator_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tournaments_creator_status_created",
        "tournaments",
        ["creator_user_id", "status", "created_at"],
    )

    op.create_table(
        "tournament_participants",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("eliminated_round", sa.Integer(), nullable=True),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("eliminated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tournament_id", "seed", name="uq_tournament_participant_seed"),
        sa.UniqueConstraint("tournament_id", "user_id", name="uq_tournament_participant_user"),
    )
    op.create_index(
        "ix_tournament_participants_user_status",
        "tournament_participants",
        ["user_id", "status"],
    )

    op.create_table(
        "tournament_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tournament_id", "round_number", name="uq_tournament_round_number"),
    )
    op.create_index(
        "ix_tournament_rounds_tournament_number",
        "tournament_rounds",
        ["tournament_id", "round_number"],
    )

    op.create_table(
        "tournament_bracket_matches",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tournament_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("round_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("bracket_position", sa.Integer(), nullable=False),
        sa.Column("left_participant_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("right_participant_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("winner_participant_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("loser_participant_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("next_bracket_match_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("next_slot", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["left_participant_id"], ["tournament_participants.id"]),
        sa.ForeignKeyConstraint(["loser_participant_id"], ["tournament_participants.id"]),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["next_bracket_match_id"], ["tournament_bracket_matches.id"]),
        sa.ForeignKeyConstraint(["right_participant_id"], ["tournament_participants.id"]),
        sa.ForeignKeyConstraint(["round_id"], ["tournament_rounds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["winner_participant_id"], ["tournament_participants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", name="uq_tournament_bracket_match"),
        sa.UniqueConstraint("round_id", "bracket_position", name="uq_tournament_bracket_position"),
    )
    op.create_index(
        "ix_tournament_bracket_tournament_status",
        "tournament_bracket_matches",
        ["tournament_id", "status"],
    )
    op.create_index("ix_tournament_bracket_match_id", "tournament_bracket_matches", ["match_id"])


def downgrade() -> None:
    op.drop_index("ix_tournament_bracket_match_id", table_name="tournament_bracket_matches")
    op.drop_index("ix_tournament_bracket_tournament_status", table_name="tournament_bracket_matches")
    op.drop_table("tournament_bracket_matches")
    op.drop_index("ix_tournament_rounds_tournament_number", table_name="tournament_rounds")
    op.drop_table("tournament_rounds")
    op.drop_index("ix_tournament_participants_user_status", table_name="tournament_participants")
    op.drop_table("tournament_participants")
    op.drop_index("ix_tournaments_creator_status_created", table_name="tournaments")
    op.drop_table("tournaments")
