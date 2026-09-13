# Code Blitz Database

This folder contains the first database design for Code Blitz.

## Files

- `schema.sql` - PostgreSQL database structure.
- `seed_problems.json` - original problem library seed with 100 tasks.
- `seed_courses.json` - learning course catalog seed with free and premium tracks.

## Main Tables

- `users` - accounts, rating, wins/losses.
- `problems` - problem statements and starter code.
- `problem_tags` + `problem_tag_links` - topics like Array, DP, Graph.
- `test_cases` - visible and hidden checks for each problem.
- `matches` - one blitz game session.
- `match_participants` - players/bots inside a match.
- `match_tasks` - the 6 random tasks selected for a match.
- `matchmaking_queue` - online search queue by rating.
- `submissions` - code runs and final submits.
- `submission_case_results` - per-test result details.
- `rating_events` - rating history after games.
- `ghost_runs` - saved past runs for racing against yourself.
- `courses` - free and premium programming courses.
- `course_lessons` - ordered lessons inside a course.
- `course_enrollments` - user progress and access to courses.
- `course_lesson_progress` - completed lessons per user.
- `course_practice_problems` - practice tasks attached to courses.

## Match Rule

Backend match creation should select:

- 3 easy problems
- 2 medium problems
- 1 hard problem

Then insert those rows into `match_tasks` with positions `1..6`.

Recommended order:

1. easy warm-up
2. easy different topic
3. medium
4. easy fast task
5. medium
6. hard finisher

Avoid repeating the same `concept_group` too many times in one match.

## Rating Matchmaking

See `docs/rating-matchmaking.md`.

Online search starts with a narrow rating range and widens over time:

- first 10 seconds: `+/- 100`
- then `+/- 200`
- then `+/- 350`
- long wait: `+/- 600`

## Next Backend Step

Create API endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /matches`
- `GET /matches/:id`
- `POST /submissions/run`
- `POST /submissions/submit`
