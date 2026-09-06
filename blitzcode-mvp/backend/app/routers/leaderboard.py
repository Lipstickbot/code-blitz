from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BlitzSession, User, UserStats
from app.schemas import BlitzLeaderboardEntryOut, LeaderboardEntryOut

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/global", response_model=list[LeaderboardEntryOut])
async def global_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User, UserStats)
        .join(UserStats, UserStats.user_id == User.id)
        .order_by(desc(UserStats.rating))
        .limit(limit)
    )
    rows = result.all()
    return [
        LeaderboardEntryOut(rank=i + 1, username=user.username, rating=stats.rating)
        for i, (user, stats) in enumerate(rows)
    ]


@router.get("/blitz", response_model=list[BlitzLeaderboardEntryOut])
async def blitz_leaderboard(
    duration_minutes: int | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    if duration_minutes is not None and duration_minutes not in {5, 10, 15}:
        raise HTTPException(status_code=400, detail="duration_minutes must be 5, 10 or 15")

    query = (
        select(User, BlitzSession)
        .join(BlitzSession, BlitzSession.user_id == User.id)
        .where(BlitzSession.status == "finished")
    )
    if duration_minutes:
        query = query.where(BlitzSession.duration_minutes == duration_minutes)

    result = await db.execute(
        query.order_by(
            desc(BlitzSession.total_score),
            desc(BlitzSession.problems_solved_count),
            BlitzSession.finished_at,
        )
    )

    best_by_user: dict[str, tuple[User, BlitzSession]] = {}
    for user, session in result.all():
        if user.id not in best_by_user:
            best_by_user[user.id] = (user, session)
        if len(best_by_user) >= limit:
            break

    return [
        BlitzLeaderboardEntryOut(
            rank=index + 1,
            username=user.username,
            total_score=session.total_score,
            problems_solved_count=session.problems_solved_count,
            duration_minutes=session.duration_minutes,
            finished_at=session.finished_at,
        )
        for index, (user, session) in enumerate(best_by_user.values())
    ]
