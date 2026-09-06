# Rating And Matchmaking

Code Blitz ranked online should match players by rating first, then slowly widen the search range if no opponent is found.

## Rating Model

Use a simple Elo-like system.

Default values:

```text
new user rating: 1200
K factor: 32
minimum rating: 100
```

Expected score:

```text
expected = 1 / (1 + 10 ^ ((opponent_rating - user_rating) / 400))
```

Rating update:

```text
new_rating = old_rating + K * (actual_score - expected)
```

Actual score:

```text
win  = 1
draw = 0.5
loss = 0
```

In Code Blitz, winner can be decided by:

1. More solved tasks.
2. If solved tasks are equal, faster total accepted time.
3. If still equal, draw.

## Matchmaking Queue

When a player clicks online start:

1. Read the user's current rating.
2. Insert into `matchmaking_queue`.
3. Search for another `searching` player in rating range.
4. If found, create `matches`, `match_participants`, and `match_tasks`.
5. Mark both queue rows as `matched`.

## Rating Range Expansion

Start strict, then widen:

```text
0-10 seconds:   +/- 100 rating
10-25 seconds:  +/- 200 rating
25-45 seconds:  +/- 350 rating
45+ seconds:    +/- 600 rating
```

This keeps early matches fair but prevents players waiting forever.

## SQL Match Candidate Rule

Candidate should satisfy:

```text
status = 'searching'
mode = requested mode
candidate.user_id != current user
candidate.rating_snapshot between current.rating_min and current.rating_max
current.rating_snapshot between candidate.rating_min and candidate.rating_max
```

Order by:

```text
ABS(candidate.rating_snapshot - current.rating_snapshot), candidate.queued_at
```

## Data To Save

Before match:

- `match_participants.rating_before`

After match:

- `match_participants.rating_after`
- `rating_events.rating_before`
- `rating_events.rating_after`
- `users.rating`
- `users.games_played`
- `users.wins`
- `users.losses`
