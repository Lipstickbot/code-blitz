from datetime import datetime
import re

from pydantic import BaseModel, Field, field_validator


# ---- Auth ----
class RegisterRequest(BaseModel):
    email: str
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Enter a valid email")
        return email

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        username = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_]+", username):
            raise ValueError("Username can contain only letters, numbers, and underscores")
        return username

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain at least one letter and one number")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Enter a valid email")
        return email


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    rating: int
    xp: int
    streak_count: int
    is_admin: bool

    class Config:
        from_attributes = True


# ---- Problems ----
class TestCaseIn(BaseModel):
    input: str
    expected_output: str
    is_sample: bool = False
    position: int | None = None
    input_json: object | None = None
    expected_json: object | None = None
    is_hidden: bool = True
    explanation: str | None = None


class TestCaseOut(BaseModel):
    id: str
    problem_id: str
    position: int
    input: str
    expected_output: str
    input_json: object | None = None
    expected_json: object | None = None
    is_sample: bool
    is_hidden: bool
    explanation: str | None = None

    class Config:
        from_attributes = True


class ProblemIn(BaseModel):
    slug: str | None = None
    title: str
    description: str
    statement: str | None = None
    difficulty: str
    status: str = "active"
    concept_group: str = "general"
    tags: list[str] = Field(default_factory=list)
    starter_code_js: str = "function solve() {\n  return null;\n}"
    solution_notes: str | None = None
    estimated_seconds: int = 300
    speed_score: int = 5
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256
    test_cases: list[TestCaseIn] = Field(default_factory=list)


class ProblemUpdateIn(BaseModel):
    slug: str | None = None
    title: str | None = None
    description: str | None = None
    statement: str | None = None
    difficulty: str | None = None
    status: str | None = None
    concept_group: str | None = None
    tags: list[str] | None = None
    starter_code_js: str | None = None
    solution_notes: str | None = None
    estimated_seconds: int | None = None
    speed_score: int | None = None
    time_limit_ms: int | None = None
    memory_limit_mb: int | None = None


class ProblemOut(BaseModel):
    id: str
    slug: str | None = None
    title: str
    description: str
    statement: str | None = None
    difficulty: str
    status: str = "active"
    concept_group: str = "general"
    tags: list[str]
    starter_code_js: str | None = None
    estimated_seconds: int | None = None
    speed_score: int | None = None

    class Config:
        from_attributes = True


class AdminProblemOut(ProblemOut):
    solution_notes: str | None = None


class ProblemDetailOut(ProblemOut):
    sample_tests: list[TestCaseOut] = Field(default_factory=list)


class ProblemSolutionOut(BaseModel):
    problem_id: str
    title: str
    solution_notes: str | None = None


class ProblemReviewIn(BaseModel):
    status: str
    notes: str = ""
    checklist: dict[str, object] = Field(default_factory=dict)


class ProblemReviewOut(BaseModel):
    id: str
    problem_id: str
    reviewer_user_id: str
    status: str
    notes: str
    checklist: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Learning ----
class CourseLessonOut(BaseModel):
    id: str
    position: int
    title: str
    summary: str
    content: str = ""
    checklist: list[str] = Field(default_factory=list)
    kind: str
    duration_minutes: int
    is_preview: bool
    completed: bool = False

    class Config:
        from_attributes = True


class CoursePracticeProblemOut(BaseModel):
    id: str
    slug: str | None = None
    title: str
    difficulty: str
    tags: list[str]
    position: int


class CourseOut(BaseModel):
    id: str
    slug: str
    title: str
    summary: str
    level: str
    access_type: str
    price_cents: int
    currency: str
    status: str
    tags: list[str]
    lesson_count: int = 0
    enrolled: bool = False
    progress_percent: int = 0

    class Config:
        from_attributes = True


class CourseDetailOut(CourseOut):
    lessons: list[CourseLessonOut] = Field(default_factory=list)
    practice_problems: list[CoursePracticeProblemOut] = Field(default_factory=list)


class CourseRecommendationOut(CourseOut):
    score: int
    reason: str


class CourseEnrollmentOut(BaseModel):
    course_id: str
    status: str
    progress_percent: int


class CourseLessonCompleteOut(BaseModel):
    course_id: str
    lesson_id: str
    progress_percent: int
    completed_lessons: int
    lesson_count: int


# ---- Submissions ----
class SubmissionIn(BaseModel):
    problem_id: str
    language: str
    code: str
    kind: str = "submit"
    match_id: str | None = None
    match_task_id: str | None = None
    blitz_session_id: str | None = None


class SubmissionOut(BaseModel):
    status: str  # accepted | wrong_answer | runtime_error | error
    execution_time_ms: int | None = None
    message: str | None = None
    passed_count: int = 0
    total_count: int = 0
    case_results: list[dict] = []


class JudgeLanguageOut(BaseModel):
    id: str
    label: str
    status: str
    runtime: str
    notes: str


# ---- Blitz Game ----
class BlitzStartRequest(BaseModel):
    duration_minutes: int


class BlitzStartResponse(BaseModel):
    session_id: str
    ends_at: datetime
    problem_ids: list[str]


class BlitzFinishResponse(BaseModel):
    total_score: int
    problems_solved_count: int
    duration_minutes: int


# ---- Online Matches ----
class MatchmakingJoinResponse(BaseModel):
    status: str
    match_id: str | None = None
    message: str


class MatchmakingStatusResponse(BaseModel):
    status: str
    match_id: str | None = None
    rating_min: int | None = None
    rating_max: int | None = None


class FriendRoomCreateIn(BaseModel):
    opponent_username: str = Field(min_length=3, max_length=50)


class FriendRoomOut(BaseModel):
    id: str
    match_id: str
    status: str
    creator_user_id: str
    creator_username: str
    invited_user_id: str
    invited_username: str
    created_at: datetime
    accepted_at: datetime | None = None
    expires_at: datetime | None = None


class TournamentCreateIn(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    player_usernames: list[str] = Field(min_length=1, max_length=31)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("player_usernames")
    @classmethod
    def validate_player_usernames(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for username in value:
            normalized = username.strip()
            if not normalized:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_]+", normalized):
                raise ValueError("Usernames can contain only letters, numbers, and underscores")
            if normalized in cleaned:
                raise ValueError("Duplicate usernames are not allowed")
            cleaned.append(normalized)
        return cleaned


class TournamentParticipantOut(BaseModel):
    id: str
    user_id: str
    username: str
    seed: int
    status: str
    eliminated_round: int | None = None


class TournamentBracketMatchOut(BaseModel):
    id: str
    round_number: int
    bracket_position: int
    match_id: str | None = None
    status: str
    left_participant_id: str | None = None
    right_participant_id: str | None = None
    left_username: str | None = None
    right_username: str | None = None
    winner_participant_id: str | None = None
    loser_participant_id: str | None = None
    next_bracket_match_id: str | None = None
    next_slot: str | None = None


class TournamentOut(BaseModel):
    id: str
    name: str
    status: str
    creator_user_id: str
    player_count: int
    max_players: int
    champion_user_id: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    participants: list[TournamentParticipantOut]
    bracket: list[TournamentBracketMatchOut]


class MatchParticipantOut(BaseModel):
    user_id: str | None = None
    side: str
    display_name: str
    rating_before: int | None = None
    rating_after: int | None = None
    solved_count: int
    progress_percent: float

    class Config:
        from_attributes = True


class MatchTaskOut(BaseModel):
    id: str
    position: int
    problem_id: str
    difficulty: str

    class Config:
        from_attributes = True


class MatchTaskProblemOut(BaseModel):
    match_task_id: str
    position: int
    problem_id: str
    slug: str | None = None
    title: str
    statement: str | None = None
    description: str
    difficulty: str
    tags: list[str]
    starter_code_js: str
    time_limit_ms: int
    sample_tests: list[dict]


class MatchOut(BaseModel):
    id: str
    mode: str
    status: str
    winner_user_id: str | None = None
    duration_seconds: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    participants: list[MatchParticipantOut]
    tasks: list[MatchTaskOut]

    class Config:
        from_attributes = True


class MatchFinishResponse(BaseModel):
    match_id: str
    status: str
    winner_user_id: str | None = None
    finished_at: datetime | None = None


class MatchEventOut(BaseModel):
    id: str
    user_id: str | None = None
    match_task_id: str | None = None
    type: str
    payload: dict
    created_at: datetime

    class Config:
        from_attributes = True


class MatchReplayTaskOut(BaseModel):
    match_task_id: str
    position: int
    problem_id: str
    title: str
    difficulty: str
    accepted_by_left_at: datetime | None = None
    accepted_by_right_at: datetime | None = None


class MatchReplaySubmissionOut(BaseModel):
    id: str
    user_id: str | None = None
    problem_id: str
    match_task_id: str | None = None
    kind: str
    language: str
    status: str
    passed_count: int
    total_count: int
    runtime_ms: int | None = None
    created_at: datetime


class MatchReplayOut(BaseModel):
    match: MatchOut
    tasks: list[MatchReplayTaskOut]
    events: list[MatchEventOut]
    submissions: list[MatchReplaySubmissionOut]


# ---- Admin / Anti-cheat ----
class AntiCheatSignalOut(BaseModel):
    id: str
    user_id: str | None = None
    username: str | None = None
    submission_id: str | None = None
    match_id: str | None = None
    problem_id: str | None = None
    problem_title: str | None = None
    signal_type: str
    severity: str
    payload: dict
    reviewed: bool
    created_at: datetime


class ProblemCalibrationOut(BaseModel):
    problem_id: str
    title: str
    difficulty: str
    attempts: int
    accepted: int
    acceptance_rate: float
    average_runtime_ms: int | None = None
    recommendation: str


# ---- Profile ----
class ProfileStatsOut(BaseModel):
    rating: int
    games_played: int
    wins: int
    losses: int
    draws: int
    solved_count: int
    xp: int
    current_streak: int
    best_streak: int

    class Config:
        from_attributes = True


class ProfileOut(BaseModel):
    id: str
    username: str
    is_admin: bool
    avatar_url: str | None = None
    stats: ProfileStatsOut

    class Config:
        from_attributes = True


class RatingEventOut(BaseModel):
    rating_before: int
    rating_after: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileMatchOut(BaseModel):
    match_id: str
    mode: str
    status: str
    solved_count: int
    progress_percent: float
    rating_before: int | None = None
    rating_after: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ProfileProblemHistoryOut(BaseModel):
    problem_id: str
    title: str
    difficulty: str
    seen_count: int
    solved_count: int
    failed_count: int
    best_time_ms: int | None = None
    last_seen_at: datetime | None = None
    last_solved_at: datetime | None = None


# ---- Leaderboard ----
class LeaderboardEntryOut(BaseModel):
    rank: int
    username: str
    rating: int


class BlitzLeaderboardEntryOut(BaseModel):
    rank: int
    username: str
    total_score: int
    problems_solved_count: int
    duration_minutes: int
    finished_at: datetime | None = None
