"""initial schema v2

Revision ID: 20260825_0001
Revises:
Create Date: 2026-08-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260825_0001"
down_revision = None
branch_labels = None
depends_on = None


def uuid_pk(name: str = "id") -> sa.Column:
    return sa.Column(name, postgresql.UUID(as_uuid=False), primary_key=True)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("streak_count", sa.Integer(), nullable=False),
        sa.Column("last_activity_date", sa.DateTime(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "user_stats",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("games_played", sa.Integer(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("losses", sa.Integer(), nullable=False),
        sa.Column("draws", sa.Integer(), nullable=False),
        sa.Column("solved_count", sa.Integer(), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("best_streak", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "oauth_accounts",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_user_id", sa.Text(), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        sa.UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )

    op.create_table(
        "problems",
        uuid_pk(),
        sa.Column("slug", sa.String(length=80), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("statement", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("concept_group", sa.String(length=64), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("starter_code_js", sa.Text(), nullable=False),
        sa.Column("solution_notes", sa.Text(), nullable=True),
        sa.Column("estimated_seconds", sa.Integer(), nullable=False),
        sa.Column("speed_score", sa.Integer(), nullable=False),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_problems_slug", "problems", ["slug"])

    op.create_table(
        "test_cases",
        uuid_pk(),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=True),
        sa.Column("expected_json", sa.JSON(), nullable=True),
        sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.Column("is_hidden", sa.Boolean(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "blitz_sessions",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("problems_solved_count", sa.Integer(), nullable=False),
    )

    op.create_table(
        "matches",
        uuid_pk(),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("winner_user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "blitz_session_problems",
        uuid_pk(),
        sa.Column("blitz_session_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("blitz_sessions.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("solved", sa.Boolean(), nullable=False),
        sa.Column("solved_at", sa.DateTime(), nullable=True),
        sa.Column("points_earned", sa.Integer(), nullable=False),
    )

    op.create_table(
        "match_participants",
        uuid_pk(),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("display_name", sa.String(length=48), nullable=False),
        sa.Column("rating_before", sa.Integer(), nullable=True),
        sa.Column("rating_after", sa.Integer(), nullable=True),
        sa.Column("solved_count", sa.Integer(), nullable=False),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_accepted_time_ms", sa.Integer(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("match_id", "side", name="uq_match_participant_side"),
        sa.UniqueConstraint("match_id", "user_id", name="uq_match_participant_user"),
    )

    op.create_table(
        "match_tasks",
        uuid_pk(),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=10), nullable=False),
        sa.Column("accepted_by_left_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_by_right_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("match_id", "position", name="uq_match_task_position"),
        sa.UniqueConstraint("match_id", "problem_id", name="uq_match_task_problem"),
    )

    op.create_table(
        "matchmaking_queue",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("rating_snapshot", sa.Integer(), nullable=False),
        sa.Column("rating_min", sa.Integer(), nullable=False),
        sa.Column("rating_max", sa.Integer(), nullable=False),
        sa.Column("matched_match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("queued_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("matched_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "submissions",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("match_task_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("match_tasks.id"), nullable=True),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("runtime_ms", sa.Integer(), nullable=True),
        sa.Column("memory_kb", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("blitz_session_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("blitz_sessions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "submission_case_results",
        uuid_pk(),
        sa.Column("submission_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("submissions.id"), nullable=False),
        sa.Column("test_case_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("test_cases.id"), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("actual_json", sa.JSON(), nullable=True),
        sa.Column("expected_json", sa.JSON(), nullable=True),
        sa.Column("runtime_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.UniqueConstraint("submission_id", "position", name="uq_submission_case_position"),
    )

    op.create_table(
        "match_events",
        uuid_pk(),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("match_task_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("match_tasks.id"), nullable=True),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "rating_events",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("rating_before", sa.Integer(), nullable=False),
        sa.Column("rating_after", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "user_problem_history",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("seen_count", sa.Integer(), nullable=False),
        sa.Column("solved_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("best_time_ms", sa.Integer(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("last_solved_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "problem_id", name="uq_user_problem_history"),
    )

    op.create_table(
        "user_problem_status",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("problem_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("problems.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("best_submission_id", postgresql.UUID(as_uuid=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_problem_status")
    op.drop_table("user_problem_history")
    op.drop_table("rating_events")
    op.drop_table("match_events")
    op.drop_table("submission_case_results")
    op.drop_table("submissions")
    op.drop_table("matchmaking_queue")
    op.drop_table("match_tasks")
    op.drop_table("match_participants")
    op.drop_table("blitz_session_problems")
    op.drop_table("matches")
    op.drop_table("blitz_sessions")
    op.drop_table("test_cases")
    op.drop_index("ix_problems_slug", table_name="problems")
    op.drop_table("problems")
    op.drop_table("oauth_accounts")
    op.drop_table("user_stats")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
