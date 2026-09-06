# Code Blitz: Database And Hosting Roadmap

## Current Database Shape

Database target: PostgreSQL.

The live backend source of truth is the SQLAlchemy model layer in `blitzcode-mvp/backend/app/models.py`.
The human-readable schema overview is `db/schema.sql`.
Database changes are applied through Alembic migrations in `blitzcode-mvp/backend/migrations/versions`.

## Main Tables

### Users And Auth

- `users` - accounts, email, username, password hash, role, admin flag and legacy profile fields.
- `oauth_accounts` - reserved table for future Google/GitHub login links.
- `user_stats` - rating, games played, wins, losses, solved count, XP and streaks.

Why: account data and rating data are separated so rating can grow without making the `users` table messy.

### Problems

- `problems` - task title, slug, statement, difficulty, tags, starter code, solution notes and limits.
- `test_cases` - sample and hidden tests for each task.
- `problem_reviews` - admin/editorial review status and comments.
- `user_problem_history` - per-user seen/solved/failed counts and best time.
- `user_problem_status` - simple per-user task status.

Why: tasks and tests are separate because one task can have many tests. Hidden tests stay in the backend and are used by Submit.

### Submissions And Judge

- `submissions` - every Run/Submit attempt, language, code, status and summary result.
- `submission_case_results` - result for every checked test case.
- `anti_cheat_signals` - suspicious behavior records for admin review.

Why: `submissions` stores the big result, `submission_case_results` stores details. This makes debugging and anti-cheat possible.

### Matches And Arena

- `matches` - match mode, status, timer, start/finish time and winner.
- `match_participants` - left/right players, rating before/after and progress.
- `match_tasks` - exact six-task payload for a match.
- `match_events` - timeline for replay and live progress.
- `matchmaking_queue` - users waiting for online matchmaking by rating.
- `friend_rooms` - invite rooms for playing with a friend by username.

Why: match task payload is stored separately so both players always receive the same task set.

### Learning

- `courses` - currently one published free intro course.
- `course_lessons` - lesson title, summary, content, checklist and duration.
- `course_enrollments` - user enrollment and progress percent.
- `course_lesson_progress` - completed lessons.
- `course_practice_problems` - links from course to real tasks.

Why: the learning section uses the same problem bank as Arena, so lessons can send the user into real practice.

### Older/Optional

- `blitz_sessions` and `blitz_session_problems` - older solo blitz session flow.
- `ghost_runs` - planned/older storage for racing against past self snapshots.

## Seed Files

- `db/seed_problems.json` - current task library, now 50 tasks.
- `db/seed_courses.json` - current course library, now one free intro course.
- `blitzcode-mvp/backend/seed.py` - loads seed data into PostgreSQL.

After schema changes or seed changes:

```bash
cd blitzcode-mvp/backend
alembic upgrade head
python seed.py
```

## Database Roadmap

### Phase 1: Stabilize Current MVP

- Keep PostgreSQL as the main database.
- Keep Redis for rate limits and realtime helper state.
- Keep Alembic as the only way to change schema.
- Keep seed files as the first content source for tasks and the intro course.
- Make sure every new task has sample and hidden tests.

Status: mostly done.

### Phase 2: Make Problems Production-Ready

- Add stronger admin filters for task status, difficulty, tags and quality.
- Add more problem analytics:
  - attempts;
  - acceptance rate;
  - average runtime;
  - common failed test.
- Add versioning for tasks and tests so old match results still make sense after edits.
- Expand task library from 50 to 100+ original tasks.

### Phase 3: Improve Matchmaking And Realtime

- Add WebSocket invite notifications for friend rooms.
- Add rematch flow.
- Add queue cancellation cleanup.
- Add stronger rating windows:
  - close rating first;
  - expand range over time;
  - avoid repeated same opponent.
- Add match timeout cleanup job.

### Phase 4: Learning System

- Keep one free intro course now.
- Later add more free programming courses only when the core Arena is stable.
- Add personalized recommendations based on:
  - failed tags;
  - slow solved tasks;
  - rating range;
  - recently ignored topics.
- Add lesson content editor in Admin.

### Phase 5: Security And Scale

- Move judge execution into a separate worker service.
- Add stronger sandbox limits for CPU, memory and network.
- Add database backups.
- Add audit logs for admin actions.
- Add monitoring for API, database, Redis and judge failures.

## Hosting Plan

Recommended first real setup:

- GitHub repository for source code.
- One Linux VPS for staging.
- Docker Compose on the server.
- PostgreSQL container.
- Redis container.
- FastAPI backend container.
- Caddy reverse proxy for HTTPS.
- Static frontend served by Caddy from the repository root.

The project already has staging files:

- `blitzcode-mvp/backend/docker-compose.staging.yml`
- `blitzcode-mvp/backend/Caddyfile.staging`
- `blitzcode-mvp/backend/.env.staging.example`
- `blitzcode-mvp/backend/scripts/check_staging.py`
- `blitzcode-mvp/backend/scripts/deploy_staging.sh`
- `.github/workflows/ci-cd.yml`

## Git Workflow

### One-Time GitHub Setup

Create a GitHub repository, then from project root:

```bash
git init
git add .
git commit -m "Initial Code Blitz MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/code-blitz.git
git push -u origin main
```

### Normal Update Flow

For every future feature:

```bash
git checkout -b codex/feature-name
git add .
git commit -m "Add feature name"
git push -u origin codex/feature-name
```

Then open a Pull Request on GitHub. After checks pass, merge into `main`.

### Deploy Update Flow

When code reaches `main`, GitHub Actions can:

1. run backend tests;
2. run frontend checks;
3. build Docker image;
4. SSH into the server;
5. pull latest code;
6. run migrations;
7. restart services.

## Server Setup Roadmap

### Step 1: Buy Or Create A VPS

Use a Linux server with:

- Ubuntu LTS;
- Docker;
- Docker Compose;
- ports `80` and `443` open;
- at least 2 GB RAM for staging.

### Step 2: Point Domain

Create DNS A record:

```text
staging.your-domain.com -> SERVER_IP
```

### Step 3: Clone Repo On Server

```bash
git clone https://github.com/YOUR_USERNAME/code-blitz.git /opt/code-blitz
cd /opt/code-blitz/blitzcode-mvp/backend
cp .env.staging.example .env.staging
```

Edit `.env.staging`:

- `STAGING_DOMAIN`
- `ACME_EMAIL`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `JWT_SECRET`
- `CORS_ORIGINS`

### Step 4: Check Server Readiness

```bash
cd /opt/code-blitz/blitzcode-mvp/backend
python scripts/check_staging.py --env-file .env.staging --with-docker
```

### Step 5: First Deploy

```bash
cd /opt/code-blitz/blitzcode-mvp/backend
bash scripts/deploy_staging.sh
```

### Step 6: GitHub Secrets

Add these in GitHub repository settings:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_KEY`
- `DEPLOY_PATH`
- `DEPLOY_MODE=staging`

After that, pushing to `main` can deploy automatically.

## Important Rules

- Never commit `.env`, `.env.staging`, `.env.production` with real secrets.
- Always run `alembic upgrade head` before `python seed.py`.
- Always use migrations for schema changes.
- Keep frontend static files and backend API connected through same domain in staging.
- Keep `AUTO_CREATE_TABLES=false` in staging/production.
- Keep `RATE_LIMITER_BACKEND=redis` in staging/production.
- Keep judge isolated through Docker.

## What To Do Next

1. Put project into a real GitHub repository.
2. Clean generated/temporary files before first commit.
3. Configure `.gitignore` so datasets/logs/archives are not committed by mistake. Done in root `.gitignore`.
4. Pick a staging domain.
5. Prepare VPS with Docker.
6. Fill `.env.staging`.
7. Run first staging deploy.
8. After staging works, continue adding tasks and polish online/friend matches.

Use `docs/git-first-commit-checklist.md` before the first GitHub push.
