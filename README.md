# Code Blitz

Competitive coding platform MVP with a blitz arena, real code judging, rating, friend rooms, task library and a small learning section.

## Current Structure

```text
index.html
app.js
styles.css
config.js
assets/
db/
docs/
blitzcode-mvp/backend/
```

## Frontend

The active frontend is the static app in the repository root:

- `index.html`
- `app.js`
- `styles.css`
- `config.js`

Run it locally:

```bash
python -m http.server 51337 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:51337/index.html
```

## Backend

The backend lives in `blitzcode-mvp/backend` and uses:

- FastAPI;
- PostgreSQL;
- Redis;
- Alembic migrations;
- Docker-isolated judge execution.

See `blitzcode-mvp/backend/README.md`.

## Database

Seed files:

- `db/seed_problems.json` - 71 starter tasks;
- `db/seed_courses.json` - one free platform intro course.

Schema overview:

- `db/schema.sql`

## Docs

- `docs/roadmap.md`
- `docs/database-hosting-roadmap.md`
- `docs/staging-runbook.md`
- `docs/ci-cd.md`
