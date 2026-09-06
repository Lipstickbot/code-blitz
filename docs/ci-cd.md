# Code Blitz CI/CD

## What Runs

GitHub Actions workflow: `.github/workflows/ci-cd.yml`.

On pull requests and pushes it runs:

- backend unit checks with `python scripts/check_backend.py --with-preflight`;
- Alembic migration upgrade against a PostgreSQL service;
- Redis-backed rate limiter environment through a Redis service;
- static UI JavaScript syntax check with `node --check app.js`;
- runtime frontend config through `config.js` and staging Caddy override;
- Next frontend install and `npm run build`;
- backend Docker image build.

The backend CI also pulls judge runtime images:

- `python:3.12-alpine`
- `node:22-alpine`

That makes sure the Docker judge path is still valid.

## Deploy Secrets

Deployment only runs on `main` pushes when all required secrets exist:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_KEY`
- `DEPLOY_PATH`
- `DEPLOY_MODE` set to `staging` for the first server target

The deploy job connects over SSH, pulls the latest code, starts backend services, runs production preflight, applies Alembic migrations, and restarts `code-blitz-api`.
For the first staging target, point `DEPLOY_PATH` to the repository folder and run `blitzcode-mvp/backend/scripts/deploy_staging.sh` from the server.

## Production Server Assumptions

The target server should already have:

- Docker and Docker Compose;
- Python backend dependencies installed in the deployment environment;
- a configured `blitzcode-mvp/backend/.env.production`;
- for staging, a configured `blitzcode-mvp/backend/.env.staging`;
- DNS pointing the staging domain to the server;
- inbound ports `80` and `443` open for Caddy HTTPS;
- a systemd service named `code-blitz-api`;
- approved judge images pulled or pullable by Docker.

The first staging target can use `docs/staging-runbook.md` instead of a systemd service.
Use `docs/staging-deployment-checklist.md` when filling the first server secrets.
In staging, Caddy serves the root static frontend and proxies `/api/...` to the backend container.
Before running a staging deploy, use `python scripts/check_staging.py --env-file .env.staging --with-docker`.

## Why This Shape

CI checks code before merge. CD is intentionally gated by secrets, so this repository can be pushed safely before a production server is ready.
