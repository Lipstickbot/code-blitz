from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Match, MatchParticipant, MatchTask, MatchmakingQueue, User, UserStats
from app.services.match_lifecycle import finish_match_if_expired
from app.services.task_picker import pick_ranked_match_tasks


DEFAULT_RATING_WINDOW = 100
QUEUE_TTL_SECONDS = 90
MATCH_DURATION_SECONDS = 1800
RATING_WINDOWS = [
    (10, 100),
    (25, 200),
    (45, 350),
    (QUEUE_TTL_SECONDS, 600),
]


async def join_ranked_queue(db: AsyncSession, user: User) -> Match | None:
    active_match = await get_active_match_for_user(db, user.id)
    if active_match:
        await _cancel_existing_search(db, user.id)
        await db.commit()
        return active_match

    stats = await _get_or_create_stats(db, user)
    await _cancel_existing_search(db, user.id)

    own_queue = MatchmakingQueue(
        user_id=user.id,
        mode="online",
        status="searching",
        rating_snapshot=stats.rating,
        rating_min=stats.rating - DEFAULT_RATING_WINDOW,
        rating_max=stats.rating + DEFAULT_RATING_WINDOW,
        expires_at=datetime.utcnow() + timedelta(seconds=QUEUE_TTL_SECONDS),
    )
    db.add(own_queue)
    await db.flush()

    candidate = await _find_candidate(db, user.id, stats.rating, own_queue.rating_min, own_queue.rating_max)
    if candidate is None:
        await db.commit()
        return None

    match = await _create_match_from_queue(db, own_queue, candidate)
    await db.commit()
    await db.refresh(match)
    return match


async def refresh_ranked_queue(db: AsyncSession, user: User) -> MatchmakingQueue | Match | None:
    active_match = await get_active_match_for_user(db, user.id)
    if active_match:
        return active_match

    result = await db.execute(
        select(MatchmakingQueue)
        .where(
            MatchmakingQueue.user_id == user.id,
            MatchmakingQueue.status == "searching",
        )
        .order_by(MatchmakingQueue.queued_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if row is None:
        return None

    now = datetime.utcnow()
    if row.expires_at and now > row.expires_at:
        row.status = "expired"
        await db.commit()
        return row

    _expand_rating_window(row, now)
    candidate = await _find_candidate(db, row.user_id, row.rating_snapshot, row.rating_min, row.rating_max)
    if candidate is None:
        await db.commit()
        return row

    match = await _create_match_from_queue(db, row, candidate)
    await db.commit()
    await db.refresh(match)
    return match


async def cancel_ranked_queue(db: AsyncSession, user_id: str) -> bool:
    changed = await _cancel_existing_search(db, user_id)
    await db.commit()
    return changed


async def get_active_match_for_user(db: AsyncSession, user_id: str) -> Match | None:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.participants), selectinload(Match.tasks))
        .join(MatchParticipant, MatchParticipant.match_id == Match.id)
        .where(MatchParticipant.user_id == user_id, Match.status == "active")
        .order_by(Match.created_at.desc())
        .limit(1)
    )
    match = result.scalar_one_or_none()
    if not match:
        return None
    if await finish_match_if_expired(db, match):
        await db.commit()
        return None
    return match


async def _get_or_create_stats(db: AsyncSession, user: User) -> UserStats:
    stats = await db.get(UserStats, user.id)
    if stats:
        return stats
    stats = UserStats(user_id=user.id, rating=user.rating or 1200)
    db.add(stats)
    await db.flush()
    return stats


async def _cancel_existing_search(db: AsyncSession, user_id: str) -> bool:
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == user_id,
            MatchmakingQueue.status == "searching",
        )
    )
    active_rows = result.scalars().all()
    for row in active_rows:
        row.status = "cancelled"
    return bool(active_rows)


async def _find_candidate(
    db: AsyncSession,
    user_id: str,
    rating: int,
    rating_min: int,
    rating_max: int,
) -> MatchmakingQueue | None:
    result = await db.execute(
        select(MatchmakingQueue)
        .where(
            MatchmakingQueue.status == "searching",
            MatchmakingQueue.mode == "online",
            MatchmakingQueue.user_id != user_id,
            MatchmakingQueue.rating_snapshot >= rating_min,
            MatchmakingQueue.rating_snapshot <= rating_max,
            MatchmakingQueue.rating_min <= rating,
            MatchmakingQueue.rating_max >= rating,
        )
        .order_by(func.abs(MatchmakingQueue.rating_snapshot - rating), MatchmakingQueue.queued_at)
        .limit(1)
    )
    return result.scalar_one_or_none()


def _expand_rating_window(row: MatchmakingQueue, now: datetime) -> None:
    elapsed = max(0, (now - row.queued_at).total_seconds()) if row.queued_at else 0
    window = RATING_WINDOWS[-1][1]
    for max_seconds, rating_window in RATING_WINDOWS:
        if elapsed <= max_seconds:
            window = rating_window
            break
    row.rating_min = row.rating_snapshot - window
    row.rating_max = row.rating_snapshot + window


async def _create_match_from_queue(
    db: AsyncSession,
    current: MatchmakingQueue,
    candidate: MatchmakingQueue,
) -> Match:
    left_user = await db.get(User, candidate.user_id)
    right_user = await db.get(User, current.user_id)
    left_stats = await db.get(UserStats, candidate.user_id)
    right_stats = await db.get(UserStats, current.user_id)

    match = Match(
        mode="online",
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
                user_id=left_user.id,
                side="left",
                display_name=left_user.username,
                rating_before=left_stats.rating if left_stats else left_user.rating,
            ),
            MatchParticipant(
                match_id=match.id,
                user_id=right_user.id,
                side="right",
                display_name=right_user.username,
                rating_before=right_stats.rating if right_stats else right_user.rating,
            ),
        ]
    )

    tasks = await pick_ranked_match_tasks(db, [left_user.id, right_user.id])
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

    current.status = "matched"
    candidate.status = "matched"
    current.matched_match_id = match.id
    candidate.matched_match_id = match.id
    current.matched_at = datetime.utcnow()
    candidate.matched_at = datetime.utcnow()

    return match
