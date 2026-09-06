-- Code Blitz target database schema v2
-- PostgreSQL
-- This schema is designed for online ranked blitz while keeping the current frontend unchanged.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE user_role AS ENUM ('player', 'admin');
CREATE TYPE auth_provider AS ENUM ('password', 'google', 'github');
CREATE TYPE problem_difficulty AS ENUM ('easy', 'medium', 'hard');
CREATE TYPE problem_status AS ENUM ('draft', 'reviewed', 'active', 'retired');
CREATE TYPE match_mode AS ENUM ('online', 'bot', 'ghost', 'solo');
CREATE TYPE match_status AS ENUM ('waiting', 'active', 'finished', 'cancelled', 'expired');
CREATE TYPE participant_side AS ENUM ('left', 'right');
CREATE TYPE queue_status AS ENUM ('searching', 'matched', 'cancelled', 'expired');
CREATE TYPE submission_kind AS ENUM ('run', 'submit');
CREATE TYPE submission_status AS ENUM ('queued', 'running', 'accepted', 'wrong_answer', 'runtime_error', 'time_limit', 'compile_error');
CREATE TYPE match_event_type AS ENUM ('match_started', 'task_opened', 'run_finished', 'task_accepted', 'match_finished', 'player_left');

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(32) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash TEXT,
  role user_role NOT NULL DEFAULT 'player',
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE oauth_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider auth_provider NOT NULL,
  provider_user_id TEXT NOT NULL,
  provider_email VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (provider, provider_user_id),
  UNIQUE (user_id, provider)
);

CREATE TABLE user_stats (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL DEFAULT 1200,
  games_played INTEGER NOT NULL DEFAULT 0,
  wins INTEGER NOT NULL DEFAULT 0,
  losses INTEGER NOT NULL DEFAULT 0,
  draws INTEGER NOT NULL DEFAULT 0,
  solved_count INTEGER NOT NULL DEFAULT 0,
  current_streak INTEGER NOT NULL DEFAULT 0,
  best_streak INTEGER NOT NULL DEFAULT 0,
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
  status problem_status NOT NULL DEFAULT 'draft',
  concept_group VARCHAR(64) NOT NULL,
  statement TEXT NOT NULL,
  starter_code_js TEXT NOT NULL,
  starter_code_py TEXT,
  solution_notes TEXT,
  estimated_seconds INTEGER NOT NULL DEFAULT 300,
  speed_score INTEGER NOT NULL DEFAULT 5 CHECK (speed_score BETWEEN 1 AND 10),
  time_limit_ms INTEGER NOT NULL DEFAULT 2000,
  memory_limit_mb INTEGER NOT NULL DEFAULT 256,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
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
  is_sample BOOLEAN NOT NULL DEFAULT false,
  is_hidden BOOLEAN NOT NULL DEFAULT true,
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
  solved_count INTEGER NOT NULL DEFAULT 0,
  progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
  total_accepted_time_ms INTEGER NOT NULL DEFAULT 0,
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
  accepted_by_left_at TIMESTAMPTZ,
  accepted_by_right_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (match_id, position),
  UNIQUE (match_id, problem_id)
);

CREATE TABLE matchmaking_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mode match_mode NOT NULL DEFAULT 'online',
  status queue_status NOT NULL DEFAULT 'searching',
  rating_snapshot INTEGER NOT NULL,
  rating_min INTEGER NOT NULL,
  rating_max INTEGER NOT NULL,
  matched_match_id UUID REFERENCES matches(id) ON DELETE SET NULL,
  queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  matched_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '90 seconds')
);

CREATE TABLE submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
  match_task_id UUID REFERENCES match_tasks(id) ON DELETE SET NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE RESTRICT,
  kind submission_kind NOT NULL,
  language VARCHAR(32) NOT NULL DEFAULT 'javascript',
  code TEXT NOT NULL,
  status submission_status NOT NULL DEFAULT 'queued',
  passed_count INTEGER NOT NULL DEFAULT 0,
  total_count INTEGER NOT NULL DEFAULT 0,
  runtime_ms INTEGER,
  memory_kb INTEGER,
  error_message TEXT,
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

CREATE TABLE match_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  match_task_id UUID REFERENCES match_tasks(id) ON DELETE SET NULL,
  type match_event_type NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
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

CREATE TABLE user_problem_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
  seen_count INTEGER NOT NULL DEFAULT 0,
  solved_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  best_time_ms INTEGER,
  last_seen_at TIMESTAMPTZ,
  last_solved_at TIMESTAMPTZ,
  UNIQUE (user_id, problem_id)
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

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_stats_rating ON user_stats(rating DESC);
CREATE INDEX idx_problems_picker ON problems(difficulty, speed_score DESC, concept_group) WHERE status = 'active';
CREATE INDEX idx_test_cases_problem ON test_cases(problem_id, position);
CREATE INDEX idx_matches_status ON matches(status, created_at DESC);
CREATE INDEX idx_match_participants_user ON match_participants(user_id, match_id);
CREATE INDEX idx_match_tasks_match ON match_tasks(match_id, position);
CREATE INDEX idx_matchmaking_queue_search ON matchmaking_queue(status, mode, rating_snapshot, queued_at);
CREATE UNIQUE INDEX idx_matchmaking_one_active_user ON matchmaking_queue(user_id) WHERE status = 'searching';
CREATE INDEX idx_submissions_match_user ON submissions(match_id, user_id, created_at DESC);
CREATE INDEX idx_submissions_problem ON submissions(problem_id, created_at DESC);
CREATE INDEX idx_match_events_match ON match_events(match_id, created_at);
CREATE INDEX idx_rating_events_user ON rating_events(user_id, created_at DESC);
CREATE INDEX idx_user_problem_history_recent ON user_problem_history(user_id, last_seen_at DESC);
