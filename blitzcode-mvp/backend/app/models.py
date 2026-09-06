import uuid
from datetime import datetime

from sqlalchemy import JSON, Numeric, String, Text, Integer, Boolean, ForeignKey, DateTime, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="player")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Legacy compatibility fields. New ranked data also lives in user_stats.
    rating: Mapped[int] = mapped_column(Integer, default=1200)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    stats: Mapped["UserStats"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(20))
    provider_user_id: Mapped[str] = mapped_column(Text)
    provider_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, default=1200)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    solved_count: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="stats")


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    slug: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(10))  # easy | medium | hard
    status: Mapped[str] = mapped_column(String(20), default="active")
    concept_group: Mapped[str] = mapped_column(String(64), default="general")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    starter_code_js: Mapped[str] = mapped_column(Text, default="function solve() {\n  return null;\n}")
    solution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_seconds: Mapped[int] = mapped_column(Integer, default=300)
    speed_score: Mapped[int] = mapped_column(Integer, default=5)
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=1000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256)
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="problem", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    position: Mapped[int] = mapped_column(Integer, default=0)
    input: Mapped[str] = mapped_column(Text)
    expected_output: Mapped[str] = mapped_column(Text)
    input_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    expected_json: Mapped[dict | list | int | float | str | bool | None] = mapped_column(JSON, nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    problem: Mapped["Problem"] = relationship(back_populates="test_cases")


class ProblemReview(Base):
    __tablename__ = "problem_reviews"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id", ondelete="CASCADE"))
    reviewer_user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str] = mapped_column(Text, default="")
    checklist: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(20), default="beginner")
    access_type: Mapped[str] = mapped_column(String(20), default="free")
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    status: Mapped[str] = mapped_column(String(20), default="published")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    lessons: Mapped[list["CourseLesson"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class CourseLesson(Base):
    __tablename__ = "course_lessons"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_course_lesson_position"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("courses.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    checklist: Mapped[list[str]] = mapped_column(JSON, default=list)
    kind: Mapped[str] = mapped_column(String(20), default="lesson")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=10)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="lessons")


class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_course_enrollment_user_course"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("courses.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), default="active")
    source: Mapped[str] = mapped_column(String(20), default="free")
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class CourseLessonProgress(Base):
    __tablename__ = "course_lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_course_lesson_progress_user_lesson"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("courses.id", ondelete="CASCADE"))
    lesson_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("course_lessons.id", ondelete="CASCADE"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CoursePracticeProblem(Base):
    __tablename__ = "course_practice_problems"
    __table_args__ = (
        UniqueConstraint("course_id", "problem_id", name="uq_course_practice_problem"),
        UniqueConstraint("course_id", "position", name="uq_course_practice_position"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    course_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("courses.id", ondelete="CASCADE"))
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    match_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"), nullable=True)
    match_task_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("match_tasks.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(20), default="submit")
    language: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memory_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    blitz_session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("blitz_sessions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    mode: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="waiting")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=1800)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    winner_user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    participants: Mapped[list["MatchParticipant"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    tasks: Mapped[list["MatchTask"]] = relationship(back_populates="match", cascade="all, delete-orphan")


class MatchParticipant(Base):
    __tablename__ = "match_participants"
    __table_args__ = (
        UniqueConstraint("match_id", "side", name="uq_match_participant_side"),
        UniqueConstraint("match_id", "user_id", name="uq_match_participant_user"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    side: Mapped[str] = mapped_column(String(10))
    display_name: Mapped[str] = mapped_column(String(48))
    rating_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    solved_count: Mapped[int] = mapped_column(Integer, default=0)
    progress_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    total_accepted_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    match: Mapped["Match"] = relationship(back_populates="participants")


class MatchTask(Base):
    __tablename__ = "match_tasks"
    __table_args__ = (
        UniqueConstraint("match_id", "position", name="uq_match_task_position"),
        UniqueConstraint("match_id", "problem_id", name="uq_match_task_problem"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"))
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    position: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[str] = mapped_column(String(10))
    accepted_by_left_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    accepted_by_right_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    match: Mapped["Match"] = relationship(back_populates="tasks")


class MatchmakingQueue(Base):
    __tablename__ = "matchmaking_queue"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(20), default="online")
    status: Mapped[str] = mapped_column(String(20), default="searching")
    rating_snapshot: Mapped[int] = mapped_column(Integer)
    rating_min: Mapped[int] = mapped_column(Integer)
    rating_max: Mapped[int] = mapped_column(Integer)
    matched_match_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"), nullable=True)
    queued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    matched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class FriendRoom(Base):
    __tablename__ = "friend_rooms"
    __table_args__ = (
        UniqueConstraint("match_id", name="uq_friend_room_match"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"))
    creator_user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    invited_user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SubmissionCaseResult(Base):
    __tablename__ = "submission_case_results"
    __table_args__ = (UniqueConstraint("submission_id", "position", name="uq_submission_case_position"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    submission_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("submissions.id"))
    test_case_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("test_cases.id"), nullable=True)
    position: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    actual_json: Mapped[dict | list | int | float | str | bool | None] = mapped_column(JSON, nullable=True)
    expected_json: Mapped[dict | list | int | float | str | bool | None] = mapped_column(JSON, nullable=True)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class AntiCheatSignal(Base):
    __tablename__ = "anti_cheat_signals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    submission_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("submissions.id"), nullable=True)
    match_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"), nullable=True)
    problem_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"), nullable=True)
    signal_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20), default="low")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    match_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"))
    user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    match_task_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("match_tasks.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RatingEvent(Base):
    __tablename__ = "rating_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    match_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("matches.id"), nullable=True)
    rating_before: Mapped[int] = mapped_column(Integer)
    rating_after: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserProblemHistory(Base):
    __tablename__ = "user_problem_history"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_user_problem_history"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    seen_count: Mapped[int] = mapped_column(Integer, default=0)
    solved_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    best_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_solved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BlitzSession(Base):
    __tablename__ = "blitz_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress | finished
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    problems_solved_count: Mapped[int] = mapped_column(Integer, default=0)

    session_problems: Mapped[list["BlitzSessionProblem"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class BlitzSessionProblem(Base):
    __tablename__ = "blitz_session_problems"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    blitz_session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("blitz_sessions.id"))
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    order_index: Mapped[int] = mapped_column(Integer)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    solved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped["BlitzSession"] = relationship(back_populates="session_problems")


class UserProblemStatus(Base):
    __tablename__ = "user_problem_status"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    problem_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("problems.id"))
    status: Mapped[str] = mapped_column(String(20), default="none")  # none | attempted | solved
    best_submission_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)


Index("ix_user_stats_rating", UserStats.rating)
Index("ix_problems_status_difficulty_created", Problem.status, Problem.difficulty, Problem.created_at)
Index("ix_problems_tags_gin", Problem.tags, postgresql_using="gin")
Index("ix_test_cases_problem_sample_position", TestCase.problem_id, TestCase.is_sample, TestCase.position)
Index("ix_test_cases_problem_hidden_position", TestCase.problem_id, TestCase.is_hidden, TestCase.position)
Index("ix_problem_reviews_problem_created", ProblemReview.problem_id, ProblemReview.created_at)
Index("ix_problem_reviews_reviewer_created", ProblemReview.reviewer_user_id, ProblemReview.created_at)
Index("ix_courses_status_access_level", Course.status, Course.access_type, Course.level)
Index("ix_courses_tags_gin", Course.tags, postgresql_using="gin")
Index("ix_course_lessons_course_position", CourseLesson.course_id, CourseLesson.position)
Index("ix_course_enrollments_user_status", CourseEnrollment.user_id, CourseEnrollment.status)
Index("ix_course_lesson_progress_user_course", CourseLessonProgress.user_id, CourseLessonProgress.course_id)
Index("ix_course_practice_problems_course_position", CoursePracticeProblem.course_id, CoursePracticeProblem.position)
Index("ix_blitz_sessions_user_status_started", BlitzSession.user_id, BlitzSession.status, BlitzSession.started_at)
Index(
    "ix_blitz_sessions_leaderboard",
    BlitzSession.status,
    BlitzSession.duration_minutes,
    BlitzSession.total_score,
    BlitzSession.problems_solved_count,
)
Index("ix_matches_status_created", Match.status, Match.created_at)
Index("ix_match_participants_user_match", MatchParticipant.user_id, MatchParticipant.match_id)
Index("ix_match_tasks_match_position", MatchTask.match_id, MatchTask.position)
Index("ix_matchmaking_queue_status_rating_queued", MatchmakingQueue.status, MatchmakingQueue.rating_snapshot, MatchmakingQueue.queued_at)
Index("ix_matchmaking_queue_user_status_queued", MatchmakingQueue.user_id, MatchmakingQueue.status, MatchmakingQueue.queued_at)
Index("ix_friend_rooms_invited_status_created", FriendRoom.invited_user_id, FriendRoom.status, FriendRoom.created_at)
Index("ix_friend_rooms_creator_status_created", FriendRoom.creator_user_id, FriendRoom.status, FriendRoom.created_at)
Index("ix_submissions_user_created", Submission.user_id, Submission.created_at)
Index("ix_submissions_problem_created", Submission.problem_id, Submission.created_at)
Index("ix_submissions_match_task_created", Submission.match_id, Submission.match_task_id, Submission.created_at)
Index("ix_submission_case_results_submission_position", SubmissionCaseResult.submission_id, SubmissionCaseResult.position)
Index("ix_anti_cheat_signals_user_created", AntiCheatSignal.user_id, AntiCheatSignal.created_at)
Index("ix_anti_cheat_signals_match_created", AntiCheatSignal.match_id, AntiCheatSignal.created_at)
Index("ix_anti_cheat_signals_type_reviewed", AntiCheatSignal.signal_type, AntiCheatSignal.reviewed)
Index("ix_match_events_match_created", MatchEvent.match_id, MatchEvent.created_at)
Index("ix_rating_events_user_created", RatingEvent.user_id, RatingEvent.created_at)
Index("ix_user_problem_history_user_seen", UserProblemHistory.user_id, UserProblemHistory.last_seen_at)
