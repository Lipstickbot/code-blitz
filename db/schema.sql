-- Code Blitz database schema
-- Target database: PostgreSQL

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE user_role AS ENUM ('player', 'admin');
CREATE TYPE problem_difficulty AS ENUM ('easy', 'medium', 'hard');
CREATE TYPE match_mode AS ENUM ('online', 'bot', 'ghost', 'solo', 'friend', 'tournament');
CREATE TYPE match_status AS ENUM ('waiting', 'active', 'finished', 'cancelled', 'expired');
CREATE TYPE participant_side AS ENUM ('left', 'right');
CREATE TYPE submission_status AS ENUM ('queued', 'running', 'accepted', 'wrong_answer', 'runtime_error', 'time_limit');
CREATE TYPE queue_status AS ENUM ('searching', 'matched', 'cancelled', 'expired');
CREATE TYPE friend_room_status AS ENUM ('pending', 'accepted', 'cancelled', 'expired');
CREATE TYPE course_access_type AS ENUM ('free', 'premium');
CREATE TYPE course_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE course_status AS ENUM ('draft', 'published', 'archived');

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(32) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role user_role NOT NULL DEFAULT 'player',
  rating INTEGER NOT NULL DEFAULT 1200,
  games_played INTEGER NOT NULL DEFAULT 0,
  wins INTEGER NOT NULL DEFAULT 0,
  losses INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE problem_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(48) NOT NULL UNIQUE
);

CREATE TABLE problems (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(80) NOT NULL UNIQUE,
  title VARCHAR(120) NOT NULL,
  difficulty problem_difficulty NOT NULL,
  concept_group VARCHAR(64) NOT NULL,
  statement TEXT NOT NULL,
  starter_code_js TEXT NOT NULL,
  solution_notes TEXT,
  estimated_seconds INTEGER NOT NULL DEFAULT 300,
  speed_score INTEGER NOT NULL DEFAULT 5 CHECK (speed_score >= 1 AND speed_score <= 10),
  time_limit_ms INTEGER NOT NULL DEFAULT 2000,
  memory_limit_mb INTEGER NOT NULL DEFAULT 256,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE problem_tag_links (
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  tag_id UUID NOT NULL REFERENCES problem_tags(id) ON DELETE CASCADE,
  PRIMARY KEY (problem_id, tag_id)
);

CREATE TABLE test_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  input_json JSONB NOT NULL,
  expected_json JSONB NOT NULL,
  is_hidden BOOLEAN NOT NULL DEFAULT false,
  explanation TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (problem_id, position)
);

CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mode match_mode NOT NULL,
  status match_status NOT NULL DEFAULT 'waiting',
  duration_seconds INTEGER NOT NULL DEFAULT 1800,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  winner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE match_participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  side participant_side NOT NULL,
  display_name VARCHAR(48) NOT NULL,
  rating_before INTEGER,
  rating_after INTEGER,
  progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
  finished_at TIMESTAMPTZ,
  UNIQUE (match_id, side),
  UNIQUE (match_id, user_id)
);

CREATE TABLE match_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE RESTRICT,
  position INTEGER NOT NULL,
  difficulty problem_difficulty NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (match_id, position),
  UNIQUE (match_id, problem_id)
);

CREATE TABLE matchmaking_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mode match_mode NOT NULL DEFAULT 'online',
  status friend_room_status NOT NULL DEFAULT 'pending',
  rating_snapshot INTEGER NOT NULL,
  rating_min INTEGER NOT NULL,
  rating_max INTEGER NOT NULL,
  matched_match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
  queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  matched_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '90 seconds'),
  UNIQUE (user_id, status)
);

CREATE TABLE friend_rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
  creator_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  invited_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status queue_status NOT NULL DEFAULT 'searching',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  accepted_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ
);

CREATE TABLE tournaments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(120) NOT NULL,
  creator_user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  max_players INTEGER NOT NULL DEFAULT 32,
  player_count INTEGER NOT NULL,
  champion_user_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ
);

CREATE TABLE tournament_participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  seed INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  eliminated_round INTEGER,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  eliminated_at TIMESTAMPTZ,
  UNIQUE (tournament_id, user_id),
  UNIQUE (tournament_id, seed)
);

CREATE TABLE tournament_rounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
  round_number INTEGER NOT NULL,
  name VARCHAR(40) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'waiting',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  UNIQUE (tournament_id, round_number)
);

CREATE TABLE tournament_bracket_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
  round_id UUID NOT NULL REFERENCES tournament_rounds(id) ON DELETE CASCADE,
  match_id UUID UNIQUE REFERENCES matches(id),
  bracket_position INTEGER NOT NULL,
  left_participant_id UUID REFERENCES tournament_participants(id),
  right_participant_id UUID REFERENCES tournament_participants(id),
  winner_participant_id UUID REFERENCES tournament_participants(id),
  loser_participant_id UUID REFERENCES tournament_participants(id),
  status VARCHAR(20) NOT NULL DEFAULT 'waiting',
  next_bracket_match_id UUID REFERENCES tournament_bracket_matches(id),
  next_slot VARCHAR(10),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  UNIQUE (round_id, bracket_position)
);

CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug VARCHAR(100) NOT NULL UNIQUE,
  title VARCHAR(200) NOT NULL,
  summary TEXT NOT NULL,
  level course_level NOT NULL DEFAULT 'beginner',
  access_type course_access_type NOT NULL DEFAULT 'free',
  price_cents INTEGER NOT NULL DEFAULT 0 CHECK (price_cents >= 0),
  currency VARCHAR(10) NOT NULL DEFAULT 'USD',
  status course_status NOT NULL DEFAULT 'published',
  tags TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE course_lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  title VARCHAR(200) NOT NULL,
  summary TEXT NOT NULL DEFAULT '',
  content TEXT NOT NULL DEFAULT '',
  checklist JSONB NOT NULL DEFAULT '[]'::jsonb,
  kind VARCHAR(20) NOT NULL DEFAULT 'lesson',
  duration_minutes INTEGER NOT NULL DEFAULT 10,
  is_preview BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (course_id, position)
);

CREATE TABLE course_enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  source VARCHAR(20) NOT NULL DEFAULT 'free',
  progress_percent INTEGER NOT NULL DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
  enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, course_id)
);

CREATE TABLE course_lesson_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  lesson_id UUID NOT NULL REFERENCES course_lessons(id) ON DELETE CASCADE,
  completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, lesson_id)
);

CREATE TABLE course_practice_problems (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (course_id, problem_id),
  UNIQUE (course_id, position)
);

CREATE TABLE submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE RESTRICT,
  match_task_id UUID REFERENCES match_tasks(id) ON DELETE SET NULL,
  language VARCHAR(32) NOT NULL DEFAULT 'javascript',
  code TEXT NOT NULL,
  status submission_status NOT NULL DEFAULT 'queued',
  passed_count INTEGER NOT NULL DEFAULT 0,
  total_count INTEGER NOT NULL DEFAULT 0,
  runtime_ms INTEGER,
  memory_kb INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE submission_case_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
  test_case_id UUID REFERENCES test_cases(id) ON DELETE SET NULL,
  position INTEGER NOT NULL,
  status submission_status NOT NULL,
  actual_json JSONB,
  expected_json JSONB,
  runtime_ms INTEGER,
  error_message TEXT,
  UNIQUE (submission_id, position)
);

CREATE TABLE rating_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
  rating_before INTEGER NOT NULL,
  rating_after INTEGER NOT NULL,
  reason VARCHAR(80) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ghost_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  source_match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
  total_time_ms INTEGER NOT NULL,
  final_progress_percent NUMERIC(5,2) NOT NULL,
  snapshot_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_rating ON users(rating DESC);
CREATE INDEX idx_problems_difficulty ON problems(difficulty) WHERE is_active = true;
CREATE INDEX idx_problems_picker ON problems(difficulty, speed_score DESC, concept_group) WHERE is_active = true;
CREATE INDEX idx_test_cases_problem ON test_cases(problem_id, position);
CREATE INDEX idx_matches_status ON matches(status, created_at DESC);
CREATE INDEX idx_match_participants_user ON match_participants(user_id, match_id);
CREATE INDEX idx_match_tasks_match ON match_tasks(match_id, position);
CREATE INDEX idx_matchmaking_queue_search ON matchmaking_queue(status, mode, rating_snapshot, queued_at);
CREATE INDEX idx_friend_rooms_invited_status ON friend_rooms(invited_user_id, status, created_at DESC);
CREATE INDEX idx_friend_rooms_creator_status ON friend_rooms(creator_user_id, status, created_at DESC);
CREATE INDEX idx_tournaments_creator_status ON tournaments(creator_user_id, status, created_at DESC);
CREATE INDEX idx_tournament_participants_user_status ON tournament_participants(user_id, status);
CREATE INDEX idx_tournament_rounds_tournament ON tournament_rounds(tournament_id, round_number);
CREATE INDEX idx_tournament_bracket_status ON tournament_bracket_matches(tournament_id, status);
CREATE INDEX idx_tournament_bracket_match ON tournament_bracket_matches(match_id);
CREATE INDEX idx_courses_catalog ON courses(status, access_type, level);
CREATE INDEX idx_course_lessons_course ON course_lessons(course_id, position);
CREATE INDEX idx_course_enrollments_user ON course_enrollments(user_id, status);
CREATE INDEX idx_course_lesson_progress_user_course ON course_lesson_progress(user_id, course_id);
CREATE INDEX idx_course_practice_problems_course_position ON course_practice_problems(course_id, position);
CREATE INDEX idx_submissions_match_user ON submissions(match_id, user_id, created_at DESC);
CREATE INDEX idx_submissions_problem ON submissions(problem_id, created_at DESC);
CREATE INDEX idx_rating_events_user ON rating_events(user_id, created_at DESC);
