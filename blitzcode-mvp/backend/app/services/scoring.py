from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Problem, User, UserProblemHistory


DIFFICULTY_XP = {"easy": 10, "medium": 25, "hard": 50}
BLITZ_POINTS = {"easy": 100, "medium": 200, "hard": 350}


async def record_problem_result(
    db: AsyncSession,
    user: User,
    problem: Problem,
    accepted: bool,
) -> UserProblemHistory:
    """Record one judged submit and award profile progress only on first solve."""
    history = await _get_or_create_history(db, user.id, problem.id)
    history.seen_count += 1
    history.last_seen_at = datetime.utcnow()

    if not accepted:
        history.failed_count += 1
        return history

    is_first_solve = history.solved_count == 0
    history.solved_count += 1
    history.last_solved_at = datetime.utcnow()
    _update_streak(user)

    if is_first_solve:
        _award_first_solve_xp(user, problem.difficulty)

    return history


def award_training_xp(user: User, difficulty: str) -> int:
    """Legacy helper for old code paths. New submit flow uses record_problem_result."""
    xp_gained = _award_first_solve_xp(user, difficulty)
    _update_streak(user)
    return xp_gained


def award_blitz_points(user: User, difficulty: str) -> int:
    points = BLITZ_POINTS.get(difficulty, 100)
    _update_streak(user)
    return points


def _award_first_solve_xp(user: User, difficulty: str) -> int:
    xp_gained = DIFFICULTY_XP.get(difficulty, 10)
    user.xp += xp_gained
    if user.stats:
        user.stats.xp += xp_gained
        user.stats.solved_count += 1
    return xp_gained


def _update_streak(user: User) -> None:
    today = date.today()
    last = user.last_activity_date.date() if user.last_activity_date else None
    if last == today:
        pass  # already counted today
    elif last is not None and (today - last).days == 1:
        user.streak_count += 1
    else:
        user.streak_count = 1
    if user.stats:
        user.stats.current_streak = user.streak_count
        user.stats.best_streak = max(user.stats.best_streak, user.streak_count)
    user.last_activity_date = datetime.utcnow()


async def _get_or_create_history(db: AsyncSession, user_id: str, problem_id: str) -> UserProblemHistory:
    result = await db.execute(
        select(UserProblemHistory).where(
            UserProblemHistory.user_id == user_id,
            UserProblemHistory.problem_id == problem_id,
        )
    )
    history = result.scalar_one_or_none()
    if history:
        return history

    history = UserProblemHistory(user_id=user_id, problem_id=problem_id)
    db.add(history)
    return history
