from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Match, MatchEvent, MatchParticipant, MatchTask, MatchmakingQueue, User, UserStats
from app.services.match_hub import match_hub
from app.services.match_lifecycle import finish_match
from app.services.matchmaker import MATCH_DURATION_SECONDS, get_active_match_for_user


PAST_SELF_NAME = "PAST SELF"


async def create_past_self_match(db: AsyncSession, user: User) -> Match | None:
    active_match = await get_active_match_for_user(db, user.id)
    if active_match:
        return active_match

    source_match = await _find_latest_replay_source(db, user.id)
    if not source_match:
        return None

    source_tasks = await _source_tasks(db, source_match.id)
    if not source_tasks:
        return None
    if not await _has_source_progress(db, source_match.id, user.id):
        return None

    await _cancel_open_searches(db, user.id)
    stats = await db.get(UserStats, user.id)
    if not stats:
        stats = UserStats(user_id=user.id, rating=user.rating or 1200)
        db.add(stats)
        await db.flush()

    match = Match(
        mode="past_self",
        status="active",
        duration_seconds=source_match.duration_seconds or MATCH_DURATION_SECONDS,
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
                display_name=PAST_SELF_NAME,
                rating_before=stats.rating,
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

    new_tasks: list[MatchTask] = []
    for index, source_task in enumerate(source_tasks):
        new_tasks.append(
            MatchTask(
                match_id=match.id,
                problem_id=source_task.problem_id,
                position=index + 1,
                difficulty=source_task.difficulty,
            )
        )
    db.add_all(new_tasks)
    await db.flush()

    schedule = await _build_source_schedule(db, source_match, source_tasks, new_tasks, user.id)
    db.add(
        MatchEvent(
            match_id=match.id,
            user_id=None,
            type="past_self_match_started",
            payload={
                "source_match_id": source_match.id,
                "ghost_name": PAST_SELF_NAME,
                "schedule": schedule,
            },
        )
    )

    await db.commit()
    await db.refresh(match)
    return match


async def advance_past_self_match(db: AsyncSession, match: Match) -> bool:
    if match.mode != "past_self" or match.status != "active" or not match.started_at:
        return False

    start_event = await _past_self_start_event(db, match.id)
    schedule = start_event.payload.get("schedule", []) if start_event else []
    if not schedule:
        return False

    ghost_result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match.id,
            MatchParticipant.user_id.is_(None),
        )
    )
    ghost = ghost_result.scalar_one_or_none()
    if not ghost:
        return False

    task_result = await db.execute(select(MatchTask).where(MatchTask.match_id == match.id).order_by(MatchTask.position))
    tasks = list(task_result.scalars().all())
    tasks_by_id = {task.id: task for task in tasks}
    elapsed_seconds = max(0, int((datetime.utcnow() - match.started_at).total_seconds()))
    changed = False

    for item in schedule:
        match_task_id = item.get("match_task_id")
        accept_after_seconds = int(item.get("accept_after_seconds", match.duration_seconds + 1))
        task = tasks_by_id.get(match_task_id)
        if not task or task.accepted_by_left_at or elapsed_seconds < accept_after_seconds:
            continue

        accepted_at = match.started_at + timedelta(seconds=accept_after_seconds)
        task.accepted_by_left_at = accepted_at
        ghost.solved_count += 1
        ghost.total_accepted_time_ms += accept_after_seconds * 1000
        ghost.progress_percent = round((ghost.solved_count / max(1, len(tasks))) * 100, 2)
        payload = {
            "problem_id": task.problem_id,
            "solved_count": ghost.solved_count,
            "progress_percent": float(ghost.progress_percent),
            "past_self": True,
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

    if ghost.solved_count >= len(tasks) and match.status == "active":
        ghost.finished_at = datetime.utcnow()
        await finish_match(
            db,
            match,
            reason="past_self_finished",
            winner_user_id=None,
            metadata={"winner_side": ghost.side, "winner_display_name": ghost.display_name},
        )
        changed = True

    return changed


async def _find_latest_replay_source(db: AsyncSession, user_id: str) -> Match | None:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.tasks))
        .join(MatchParticipant, MatchParticipant.match_id == Match.id)
        .where(
            MatchParticipant.user_id == user_id,
            Match.status == "finished",
            Match.started_at.is_not(None),
            Match.mode.in_(["online", "bot", "past_self"]),
        )
        .order_by(desc(Match.finished_at), desc(Match.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _source_tasks(db: AsyncSession, match_id: str) -> list[MatchTask]:
    result = await db.execute(select(MatchTask).where(MatchTask.match_id == match_id).order_by(MatchTask.position))
    return list(result.scalars().all())


async def _has_source_progress(db: AsyncSession, match_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(MatchEvent.id)
        .where(
            MatchEvent.match_id == match_id,
            MatchEvent.user_id == user_id,
            MatchEvent.type == "task_accepted",
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


async def _build_source_schedule(
    db: AsyncSession,
    source_match: Match,
    source_tasks: list[MatchTask],
    new_tasks: list[MatchTask],
    user_id: str,
) -> list[dict]:
    result = await db.execute(
        select(MatchEvent)
        .where(
            MatchEvent.match_id == source_match.id,
            MatchEvent.user_id == user_id,
            MatchEvent.type == "task_accepted",
        )
        .order_by(MatchEvent.created_at)
    )
    events_by_task = {event.match_task_id: event for event in result.scalars().all()}
    schedule = []
    for source_task, new_task in zip(source_tasks, new_tasks):
        event = events_by_task.get(source_task.id)
        if not event or not source_match.started_at:
            continue
        accept_after_seconds = max(0, int((event.created_at - source_match.started_at).total_seconds()))
        schedule.append(
            {
                "match_task_id": new_task.id,
                "source_match_task_id": source_task.id,
                "accept_after_seconds": accept_after_seconds,
            }
        )
    return schedule


async def _past_self_start_event(db: AsyncSession, match_id: str) -> MatchEvent | None:
    result = await db.execute(
        select(MatchEvent)
        .where(MatchEvent.match_id == match_id, MatchEvent.type == "past_self_match_started")
        .order_by(MatchEvent.created_at)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _cancel_open_searches(db: AsyncSession, user_id: str) -> None:
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == user_id,
            MatchmakingQueue.status == "searching",
        )
    )
    for row in result.scalars().all():
        row.status = "cancelled"
