"""add indexes for frequent queries

Revision ID: 20260828_0002
Revises: 20260825_0001
Create Date: 2026-08-28
"""

from alembic import op


revision = "20260828_0002"
down_revision = "20260825_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_user_stats_rating", "user_stats", ["rating"])
    op.create_index("ix_problems_status_difficulty_created", "problems", ["status", "difficulty", "created_at"])
    op.create_index("ix_problems_tags_gin", "problems", ["tags"], postgresql_using="gin")
    op.create_index(
        "ix_test_cases_problem_sample_position",
        "test_cases",
        ["problem_id", "is_sample", "position"],
    )
    op.create_index(
        "ix_test_cases_problem_hidden_position",
        "test_cases",
        ["problem_id", "is_hidden", "position"],
    )
    op.create_index(
        "ix_blitz_sessions_user_status_started",
        "blitz_sessions",
        ["user_id", "status", "started_at"],
    )
    op.create_index(
        "ix_blitz_sessions_leaderboard",
        "blitz_sessions",
        ["status", "duration_minutes", "total_score", "problems_solved_count"],
    )
    op.create_index("ix_matches_status_created", "matches", ["status", "created_at"])
    op.create_index("ix_match_participants_user_match", "match_participants", ["user_id", "match_id"])
    op.create_index("ix_match_tasks_match_position", "match_tasks", ["match_id", "position"])
    op.create_index(
        "ix_matchmaking_queue_status_rating_queued",
        "matchmaking_queue",
        ["status", "rating_snapshot", "queued_at"],
    )
    op.create_index(
        "ix_matchmaking_queue_user_status_queued",
        "matchmaking_queue",
        ["user_id", "status", "queued_at"],
    )
    op.create_index("ix_submissions_user_created", "submissions", ["user_id", "created_at"])
    op.create_index("ix_submissions_problem_created", "submissions", ["problem_id", "created_at"])
    op.create_index(
        "ix_submissions_match_task_created",
        "submissions",
        ["match_id", "match_task_id", "created_at"],
    )
    op.create_index(
        "ix_submission_case_results_submission_position",
        "submission_case_results",
        ["submission_id", "position"],
    )
    op.create_index("ix_match_events_match_created", "match_events", ["match_id", "created_at"])
    op.create_index("ix_rating_events_user_created", "rating_events", ["user_id", "created_at"])
    op.create_index(
        "ix_user_problem_history_user_seen",
        "user_problem_history",
        ["user_id", "last_seen_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_user_problem_history_user_seen", table_name="user_problem_history")
    op.drop_index("ix_rating_events_user_created", table_name="rating_events")
    op.drop_index("ix_match_events_match_created", table_name="match_events")
    op.drop_index("ix_submission_case_results_submission_position", table_name="submission_case_results")
    op.drop_index("ix_submissions_match_task_created", table_name="submissions")
    op.drop_index("ix_submissions_problem_created", table_name="submissions")
    op.drop_index("ix_submissions_user_created", table_name="submissions")
    op.drop_index("ix_matchmaking_queue_user_status_queued", table_name="matchmaking_queue")
    op.drop_index("ix_matchmaking_queue_status_rating_queued", table_name="matchmaking_queue")
    op.drop_index("ix_match_tasks_match_position", table_name="match_tasks")
    op.drop_index("ix_match_participants_user_match", table_name="match_participants")
    op.drop_index("ix_matches_status_created", table_name="matches")
    op.drop_index("ix_blitz_sessions_leaderboard", table_name="blitz_sessions")
    op.drop_index("ix_blitz_sessions_user_status_started", table_name="blitz_sessions")
    op.drop_index("ix_test_cases_problem_hidden_position", table_name="test_cases")
    op.drop_index("ix_test_cases_problem_sample_position", table_name="test_cases")
    op.drop_index("ix_problems_tags_gin", table_name="problems")
    op.drop_index("ix_problems_status_difficulty_created", table_name="problems")
    op.drop_index("ix_user_stats_rating", table_name="user_stats")
