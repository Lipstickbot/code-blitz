#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f ".env.staging" ]; then
  echo "Missing .env.staging. Copy .env.staging.example and fill real secrets first." >&2
  exit 1
fi

STAGING_DOMAIN="$(grep -E '^STAGING_DOMAIN=' .env.staging | cut -d= -f2-)"
ACME_EMAIL="$(grep -E '^ACME_EMAIL=' .env.staging | cut -d= -f2-)"

if [ -z "$STAGING_DOMAIN" ] || [ "$STAGING_DOMAIN" = "staging.example.com" ]; then
  echo "Set STAGING_DOMAIN in .env.staging before deploying." >&2
  exit 1
fi

if [ -z "$ACME_EMAIL" ] || [ "$ACME_EMAIL" = "admin@example.com" ]; then
  echo "Set ACME_EMAIL in .env.staging before deploying." >&2
  exit 1
fi

python scripts/check_staging.py --env-file .env.staging --with-docker
docker pull python:3.12-alpine
docker pull node:22-alpine
docker compose -f docker-compose.staging.yml build api
docker compose -f docker-compose.staging.yml up -d db redis
docker compose -f docker-compose.staging.yml run --rm api python scripts/preflight_production.py --env-file .env.staging
docker compose -f docker-compose.staging.yml run --rm api alembic upgrade head
docker compose -f docker-compose.staging.yml up -d api proxy
docker compose -f docker-compose.staging.yml ps

echo "Check HTTPS readiness:"
echo "curl https://${STAGING_DOMAIN}/api/health/ready"
