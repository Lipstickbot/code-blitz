# Problem Strategy

Code Blitz needs two related systems:

1. A large problem library.
2. A fair match picker that builds a balanced set of tasks.

## Problem Sources

Best option for the platform: create original tasks based on common algorithmic patterns.

Do not copy statements from LeetCode, Codeforces, AtCoder, HackerRank, or similar sites unless the license clearly allows reuse. It is safer to write our own statements, examples, names, and test cases.

Open-source sources can be used only after checking their license. Even then, prefer rewriting the wording and keeping attribution notes in an internal admin field.

## Problem Categories

Each problem should have:

- `difficulty`: easy, medium, hard
- `tags`: array, string, stack, map, two-pointers, sliding-window, binary-search, graph, dfs, bfs, dp, greedy, heap
- `estimated_seconds`: expected solve time for a strong player
- `speed_score`: how suitable it is for blitz
- `concept_group`: broad family, used to avoid repeated task types

## Match Layout

Default ranked blitz match:

```text
6 tasks total
3 easy
2 medium
1 hard
30 minutes
```

Recommended position layout:

```text
Task 01: easy warm-up
Task 02: easy different topic
Task 03: medium
Task 04: easy fast confidence task
Task 05: medium
Task 06: hard finisher
```

This feels better than a fully random order because the player gets rhythm first, then pressure rises.

## Picker Rules

When creating a match:

1. Pick tasks by difficulty target: `3 easy + 2 medium + 1 hard`.
2. Avoid duplicate `concept_group` inside the same match when possible.
3. Avoid giving a user a problem they solved in the last 10 matches.
4. Prefer active tasks with high `speed_score`.
5. Shuffle only inside layout slots, not the entire match.
6. Use hidden tests for validation and visible tests for UI.

## Anti-Repetition Rules

Track these values per user:

- last time seen problem
- solved count
- failed count
- average solve time
- weak tags

Then the picker can:

- show weak-tag tasks more often in practice;
- avoid repeats in ranked;
- choose easier tasks for new players;
- increase hard frequency for stronger players.

## Library Growth Plan

Milestone 1:

- 40 easy
- 30 medium
- 15 hard

Milestone 2:

- 100 easy
- 80 medium
- 40 hard

Milestone 3:

- admin tool for creating tasks;
- import tool for licensed open datasets;
- automatic hidden-test generation for simple problems;
- review status: draft, reviewed, active, retired.
