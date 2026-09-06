from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Problem, UserProblemHistory


RANKED_LAYOUT = ["easy", "easy", "medium", "easy", "medium", "hard"]


async def pick_ranked_match_tasks(
    db: AsyncSession,
    user_ids: list[str],
    layout: list[str] | None = None,
) -> list[Problem]:
    """Pick a stable 6-task ranked set: 3 easy, 2 medium, 1 hard.

    The picker prefers active, blitz-friendly tasks and tries to avoid concept
    repetition and recently seen problems for both players.
    """
    target_layout = layout or RANKED_LAYOUT
    result = await db.execute(select(Problem).where(Problem.status == "active"))
    problems = list(result.scalars().all())
    if not problems:
        return []

    recently_seen = await _recently_seen_problem_ids(db, user_ids)
    by_difficulty: dict[str, list[Problem]] = defaultdict(list)
    for problem in problems:
        by_difficulty[problem.difficulty].append(problem)

    chosen: list[Problem] = []
    used_problem_ids: set[str] = set()
    used_concepts: set[str] = set()

    for difficulty in target_layout:
        candidates = by_difficulty.get(difficulty) or problems
        selected = _select_best_candidate(candidates, used_problem_ids, used_concepts, recently_seen)
        if selected is None:
            continue
        chosen.append(selected)
        used_problem_ids.add(selected.id)
        used_concepts.add(selected.concept_group)

    return chosen


async def _recently_seen_problem_ids(db: AsyncSession, user_ids: list[str]) -> set[str]:
    if not user_ids:
        return set()
    result = await db.execute(
        select(UserProblemHistory.problem_id)
        .where(UserProblemHistory.user_id.in_(user_ids))
        .order_by(UserProblemHistory.last_seen_at.desc().nullslast())
        .limit(20)
    )
    return set(result.scalars().all())


def _select_best_candidate(
    candidates: list[Problem],
    used_problem_ids: set[str],
    used_concepts: set[str],
    recently_seen: set[str],
) -> Problem | None:
    available = [problem for problem in candidates if problem.id not in used_problem_ids]
    if not available:
        return None

    def score(problem: Problem) -> tuple[int, int, int]:
        concept_penalty = 1 if problem.concept_group in used_concepts else 0
        recent_penalty = 1 if problem.id in recently_seen else 0
        return (recent_penalty, concept_penalty, -problem.speed_score)

    return sorted(available, key=score)[0]
