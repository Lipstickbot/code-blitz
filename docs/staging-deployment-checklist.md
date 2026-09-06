# Code Blitz Staging Deployment Checklist

Use this checklist when the staging server and domain are chosen. It keeps the first real deploy repeatable and avoids mixing local dev settings with server settings.

## Server

- A Linux VPS or dedicated server with public IP.
- Docker and Docker Compose installed.
- Git installed.
- Repository cloned to the deploy path, for example `/opt/code-blitz`.
- Inbound firewall allows `80/tcp` and `443/tcp`.
- The deploy user can run Docker commands.

## DNS

- Create a staging subdomain, for example `staging.codeblitz.example`.
- Point the domain A record to the server public IP.
- Wait until DNS resolves from your machine:

```bash
nslookup staging.codeblitz.example
```

## Backend Environment

On the server:

```bash
cd /opt/code-blitz/blitzcode-mvp/backend
cp .env.staging.example .env.staging
```

Fill these values in `.env.staging`:

- `STAGING_DOMAIN`: the real staging domain.
- `ACME_EMAIL`: your email for HTTPS certificate notices.
- `JWT_SECRET`: random secret, at least 32 characters.
- `POSTGRES_PASSWORD`: strong database password.
- `DATABASE_URL`: same password as `POSTGRES_PASSWORD`.
- `CORS_ORIGINS`: `https://your-staging-domain`.

Keep these values for staging safety:

- `ENVIRONMENT=staging`
- `AUTO_CREATE_TABLES=false`
- `RATE_LIMITER_BACKEND=redis`
- `JUDGE_EXECUTOR=docker`

## GitHub Actions Secrets

Add repository secrets:

- `DEPLOY_HOST`: server IP or DNS name.
- `DEPLOY_USER`: SSH user.
- `DEPLOY_KEY`: private SSH key for that user.
- `DEPLOY_PATH`: repository path on the server, for example `/opt/code-blitz`.
- `DEPLOY_MODE`: `staging`.

The deploy job only runs on `main` pushes and only when the required secrets exist.

## Preflight

Run on the server before the first deploy:

```bash
cd /opt/code-blitz/blitzcode-mvp/backend
python scripts/check_staging.py --env-file .env.staging --with-docker
```

Expected result:

- staging files exist;
- domain and email are not placeholders;
- CORS points to the staging HTTPS origin;
- Redis is required;
- Docker judge is required;
- Docker Compose staging config is valid.

## First Deploy

```bash
cd /opt/code-blitz/blitzcode-mvp/backend
bash scripts/deploy_staging.sh
```

Then check:

```bash
curl https://your-staging-domain/api/health/ready
```

Expected readiness:

- database is ok;
- rate limiter uses Redis;
- judge executor is Docker;
- frontend loads from the same HTTPS domain.

## After Deploy

- Create the first admin account with `scripts/make_admin.py`.
- Seed or review tasks through the admin screen.
- Run one real browser flow: register, login, start match, run solution, submit solution.
- Check logs if something is wrong:

```bash
docker compose --env-file .env.staging -f docker-compose.staging.yml logs --tail=100 api
docker compose --env-file .env.staging -f docker-compose.staging.yml logs --tail=100 proxy
```
