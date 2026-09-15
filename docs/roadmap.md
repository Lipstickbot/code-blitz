# Code Blitz Roadmap

## Done

- Static frontend prototype with dark/light arena UI.
- Auth endpoints: register, login, current user.
- Rating is stored in `user_stats` and shown only for authenticated users.
- Problem bank seed with 100 starter tasks.
- Admin problem CRUD and separate test case management.
- Real Python and JavaScript judge contract through `solve(...)`.
- `Run` uses up to 5 sample tests.
- `Submit` uses up to 50 hidden tests.
- Online matchmaking by rating window.
- Ranked match task layout: 3 easy, 2 medium, 1 hard.
- Match progress, finish, forfeit and Elo rating events.
- WebSocket match stream for live progress.
- Match replay backend endpoint using `match_events` and submissions.
- Profile history: rating, matches, solved problems.
- Global and Blitz leaderboards.
- API rate limits for auth, submissions and matchmaking.
- Health checks for API, database and judge runtimes.
- Alembic migrations for schema and query indexes.
- Active problem quality gate: unique slug, sample tests and hidden tests.
- Deeper problem quality checks: difficulty/status/limits/starter code validation.
- Content review flow for tasks: approved, needs_changes and comments.
- Production startup config validation.
- Production env template and deployment runbook.
- Production preflight script.
- Admin promotion and password reset script for the first trusted user.
- Database integration tests for `/api/submissions`: API request, real judge, DB persistence.
- Database integration tests for matchmaking: queue, rating pairing, match creation, active match restore.
- Frontend API error states for backend downtime, expired match, auth required and rate limits.
- Admin screen for creating/editing tasks and replacing sample/hidden tests.
- Frontend match history and replay screen connected to profile and match replay APIs.
- Redis-backed rate limiter with local memory fallback and production validation.
- Isolated Docker judge executor for Python and JavaScript submissions.
- GitHub Actions CI/CD pipeline for backend checks, static UI, Next build, Docker image and gated SSH deploy.
- First staging deployment target templates: env, Docker Compose, deploy script and runbook.
- Staging reverse proxy and HTTPS config through Caddy.
- Static frontend runtime config connected to same-origin staging API/WebSocket routing.
- Staging readiness check for env secrets, domain, CORS, Docker Compose and safety rules.
- Staging deployment checklist for server, DNS, env secrets and GitHub Actions secrets.
- Anti-cheat signal table and backend detection for very fast accepts, repeated exact code and first-submit hidden sweeps.
- Admin anti-cheat signal API and admin UI for reviewing open suspicious submissions.
- Bot opponent mode with backend match creation, shared task payload and scripted bot progress.
- Bot strategy levels with auto rating-based selection and arena difficulty selector.
- Past-self race mode that replays the user's previous accepted task timeline as a ghost opponent.
- Friend room mode: create an arena invite by username, list pending invites and start a shared match when accepted.
- Friend room cancellation and automatic invite refresh when opening Room mode.
- Copyable friend room links and background invite count refresh in the Arena mode strip.
- Learning section foundation with one free platform intro course, course lessons seed and enrollment API.
- Course detail panel and lesson completion progress tracking for enrolled free courses.
- Course practice problem links so lessons can send users into real task practice.
- TypeScript TS-light backend judge support for LeetCode-style `solve(...)` functions.
- Expanded original problem library to 100 tasks with broader tags and difficulty spread.
- Admin problem calibration API and UI using submission acceptance rate and runtime signals.
- Admin editorial review UI for approving, commenting and requesting changes on tasks.
- Admin solution notes editing for task editorials, intended approach and edge cases.
- Spoiler-safe problem editorial endpoint and arena Editorial button unlocked only after solving.
- Judge language support matrix API and frontend executable/planned language states.
- Personalized learning recommendations endpoint and Learn screen recommendation rail.
- Richer lesson content seed with theory text, checklist items and database fields.
- Tournament backend foundation: 2/4/8/16/32-player rooms, bracket rounds, automatic winner advance and final champion.
- Tournament bracket output now includes grouped rounds and rating-seeded first-round pairings through the final.
- Tournament frontend room: create cups by login list, view seeds, grouped bracket rounds and enter active matches.
- Tournament UI polish: auto-refresh, size shortcuts, player-count hints and champion banner.
- Tournament WebSocket stream for bracket update events when winners advance.
- Tournament spectator API and admin backend controls for listing/canceling tournament rooms.
- Admin tournament monitor UI with active room counts and cancel action.
- Problem bank quality tests now require 100+ tasks, balanced difficulty coverage, tags, concept groups and timing metadata.

## Next

- Choose hosting for staging, fill real server secrets and point DNS.
- Run first staging deploy and verify a real browser match flow.
- Add public/shareable tournament spectator links.

## Later

- OAuth login with Google/GitHub after local auth is stable.
- Friend-room polish: WebSocket invite notifications and rematch flow.
- Tournament polish: public/shareable spectator links and richer tournament admin audit logs.
- Learning polish: more courses later, stronger recommendation signals and premium checkout integration if paid tracks return.
- Typed adapter contract for compiled language judging: C++, Java, Go, Rust.
