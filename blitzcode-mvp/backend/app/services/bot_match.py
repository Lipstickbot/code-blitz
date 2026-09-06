from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Match, MatchEvent, MatchParticipant, MatchTask, MatchmakingQueue, User, UserStats
from app.services.match_hub import match_hub
from app.services.match_lifecycle import finish_match
from app.services.matchmaker import MATCH_DURATION_SECONDS, get_active_match_for_user
from app.services.task_picker import pick_ranked_match_tasks


BOT_NAME = "CODE BOT"
BOT_RATING = 1200
BOT_LEVELS = {"easy", "normal", "hard", "auto"}


@dataclass(frozen=True)
class BotStrategy:
    level: str
    display_name: str
    rating: int
    solve_ratios: list[float]


BOT_STRATEGIES = {
    "easy": BotStrategy("easy", "CODE BOT // EASY", 900, [0.28, 0.46, 0.66, 0.84, 0.94, 0.98]),
    "normal": BotStrategy("normal", "CODE BOT", 1200, [0.16, 0.31, 0.49, 0.68, 0.84, 0.96]),
    "hard": BotStrategy("hard", "CODE BOT // HARD", 1550, [0.08, 0.18, 0.32, 0.48, 0.66, 0.82]),
}


def resolve_bot_strategy(level: str, player_rating: int | None = None) -> BotStrategy:
    requested = (level or "auto").strip().lower()
    if requested not in BOT_LEVELS:
        requested = "auto"
    if requested != "auto":
        return BOT_STRATEGIES[requested]
    rating = player_rating or BOT_RATING
    if rating < 1050:
        return BOT_STRATEGIES["easy"]
    if rating >= 1450:
        return BOT_STRATEGIES["hard"]
    return BOT_STRATEGIES["normal"]


def bot_accept_schedule_seconds(duration_seconds: int, task_count: int, strategy: BotStrategy | None = None) -> list[int]:
    if task_count <= 0:
        return []
    duration = max(60, duration_seconds)
    ratios = (strategy or BOT_STRATEGIES["normal"]).solve_ratios
    schedule: list[int] = []
    for index in range(task_count):
        ratio = ratios[index] if index < len(ratios) else min(0.94, 0.12 + index * 0.13)
        schedule.append(min(duration - 1, max(8, int(duration * ratio))))
    return schedule


async def create_bot_match(db: AsyncSession, user: User, level: str = "auto") -> Match:
    active_match = await get_active_match_for_user(db, user.id)
    if active_match:
        return active_match
    await _cancel_open_searches(db, user.id)

    stats = await db.get(UserStats, user.id)
    if not stats:
        stats = UserStats(user_id=user.id, rating=user.rating or BOT_RATING)
        db.add(stats)
        await db.flush()
    strategy = resolve_bot_strategy(level, stats.rating)

    match = Match(
        mode="bot",
        status="active",
        duration_seconds=MATCH_DURATION_SECONDS,
        started_at=datetime.utcnow(),
    )
    db.add(match)
    await db.flush()

    db.add_all(
        [
            MatchParticipant(
                match_id=match.id,
                user_id=None,
                side="left",
                display_name=strategy.display_name,
                rating_before=strategy.rating,
            ),
            MatchParticipant(
                match_id=match.id,
                user_id=user.id,
                side="right",
                display_name=user.username,
                rating_before=stats.rating,
            ),
        ]
    )

    tasks = await pick_ranked_match_tasks(db, [user.id])
    db.add_all(
        [
            MatchTask(
                match_id=match.id,
                problem_id=problem.id,
                position=index + 1,
                difficulty=problem.difficulty,
            )
            for index, problem in enumerate(tasks)
        ]
    )

    db.add(
        MatchEvent(
            match_id=match.id,
            user_id=None,
            type="bot_match_started",
            payload={
                "bot_name": strategy.display_name,
                "bot_rating": strategy.rating,
                "bot_level": strategy.level,
            },
        )
    )
    await db.commit()
    await db.refresh(match)
    return match


async def _cancel_open_searches(db: AsyncSession, user_id: str) -> None:
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == user_id,
            MatchmakingQueue.status == "searching",
        )
    )
    for row in result.scalars().all():
        row.status = "cancelled"


async def advance_bot_match(db: AsyncSession, match: Match) -> bool:
    if match.mode != "bot" or match.status != "active" or not match.started_at:
        return False

    task_result = await db.execute(select(MatchTask).where(MatchTask.match_id == match.id).order_by(MatchTask.position))
    tasks = list(task_result.scalars().all())
    if not tasks:
        return False

    bot_result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match.id,
            MatchParticipant.user_id.is_(None),
        )
    )
    bot = bot_result.scalar_one_or_none()
    if not bot:
        return False

    now = datetime.utcnow()
    elapsed_seconds = max(0, int((now - match.started_at).total_seconds()))
    strategy = resolve_bot_strategy(_strategy_level_from_bot(bot), bot.rating_before)
    schedule = bot_accept_schedule_seconds(match.duration_seconds, len(tasks), strategy)
    changed = False

    for index, task in enumerate(tasks):
        if index >= len(schedule) or elapsed_seconds < schedule[index]:
            continue
        if task.accepted_by_left_at:
            continue

        accepted_at = match.started_at + timedelta(seconds=schedule[index])
        task.accepted_by_left_at = accepted_at
        bot.solved_count += 1
        bot.total_accepted_time_ms += schedule[index] * 1000
        bot.progress_percent = round((bot.solved_count / len(tasks)) * 100, 2)
        payload = {
            "problem_id": task.problem_id,
            "solved_count": bot.solved_count,
            "progress_percent": float(bot.progress_percent),
            "bot": True,
        }
        db.add(
            MatchEvent(
                match_id=match.id,
                user_id=None,
                match_task_id=task.id,
                type="task_accepted",
                payload=payload,
                created_at=accepted_at,
            )
        )
        await match_hub.broadcast(
            match.id,
            {
                "type": "task_accepted",
                "match_id": match.id,
                "user_id": None,
                "match_task_id": task.id,
                "payload": payload,
            },
        )
        changed = True

    if bot.solved_count >= len(tasks) and match.status == "active":
        bot.finished_at = now
        await finish_match(
            db,
            match,
            reason="bot_finished",
            winner_user_id=None,
            metadata={"winner_side": bot.side, "winner_display_name": bot.display_name},
        )
        changed = True

    return changed


def _strategy_level_from_bot(bot: MatchParticipant) -> str:
    name = (bot.display_name or "").lower()
    if "easy" in name:
        return "easy"
    if "hard" in name:
        return "hard"
    return "normal"
