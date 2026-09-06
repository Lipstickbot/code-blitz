# Code Blitz Production Runbook

## Goal

Run the backend with explicit production settings, Alembic migrations and health checks.

CI/CD setup is documented in `docs/ci-cd.md`.
Staging setup is documented in `docs/staging-runbook.md`.

## Required Settings

Use `blitzcode-mvp/backend/.env.production.example` as a template.

Important production rules:

- `ENVIRONMENT=production`
- `AUTO_CREATE_TABLES=false`
- `JWT_SECRET` must be changed and contain at least 32 characters.
- `DATABASE_URL` must point to the production PostgreSQL database.
- `REDIS_URL` must point to the production Redis instance.
- `RATE_LIMITER_BACKEND=redis`
- `JUDGE_EXECUTOR=docker`
- `JUDGE_DOCKER_BINARY` must point to a working Docker runtime.
- `JUDGE_PYTHON_IMAGE` and `JUDGE_NODE_IMAGE` must point to approved runtime images.

The backend refuses to start in production when these safety rules fail.

## Deploy Order

1. Install backend dependencies.
2. Configure environment variables from `.env.production.example`.
3. Run production preflight:

```bash
python scripts/preflight_production.py --env-file .env.production
```

4. Apply database migrations:

```bash
alembic upgrade head
```

5. Seed starter problems only when the database is empty:

```bash
python seed.py
```

6. Start the API process:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

7. Check the service:

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/ready
```

## Pre-Deploy Checklist

- Unit tests pass: `python -m unittest discover -s tests`.
- GitHub Actions CI passes on the target branch.
- Production preflight passes: `python scripts/preflight_production.py --env-file .env.production`.
- `alembic upgrade head` succeeds.
- `ENVIRONMENT=production` is set.
- `AUTO_CREATE_TABLES=false` is set.
- `JWT_SECRET` is not the default value.
- `RATE_LIMITER_BACKEND=redis` is set.
- `JUDGE_EXECUTOR=docker` is set.
- Judge runtime images are pulled on the host.
- `/api/health/ready` returns `status: ok`.

## Current Production Gaps

- Admin role is still assigned manually in the database.
