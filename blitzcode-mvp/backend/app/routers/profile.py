from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Match, MatchParticipant, Problem, RatingEvent, User, UserProblemHistory, UserStats
from app.schemas import ProfileMatchOut, ProfileOut, ProfileProblemHistoryOut, RatingEventOut


router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=ProfileOut)
async def my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = await _get_or_create_stats(db, current_user)
    return ProfileOut(
        id=current_user.id,
        username=current_user.username,
        is_admin=current_user.is_admin,
        avatar_url=current_user.avatar_url,
        stats=stats,
    )


@router.get("/me/rating-history", response_model=list[RatingEventOut])
async def my_rating_history(
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(RatingEvent)
        .where(RatingEvent.user_id == current_user.id)
        .order_by(desc(RatingEvent.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/me/matches", response_model=list[ProfileMatchOut])
async def my_match_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Match, MatchParticipant)
        .join(MatchParticipant, MatchParticipant.match_id == Match.id)
        .where(MatchParticipant.user_id == current_user.id)
        .order_by(desc(Match.created_at))
        .limit(limit)
    )
    rows = result.all()
    return [
        ProfileMatchOut(
            match_id=match.id,
            mode=match.mode,
            status=match.status,
            solved_count=participant.solved_count,
            progress_percent=float(participant.progress_percent),
            rating_before=participant.rating_before,
            rating_after=participant.rating_after,
            started_at=match.started_at,
            finished_at=match.finished_at,
        )
        for match, participant in rows
    ]


@router.get("/me/problems", response_model=list[ProfileProblemHistoryOut])
async def my_problem_history(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProblemHistory, Problem)
        .join(Problem, Problem.id == UserProblemHistory.problem_id)
        .where(UserProblemHistory.user_id == current_user.id)
        .order_by(desc(UserProblemHistory.last_seen_at))
        .limit(limit)
    )
    rows = result.all()
    return [
        ProfileProblemHistoryOut(
            problem_id=problem.id,
            title=problem.title,
            difficulty=problem.difficulty,
            seen_count=history.seen_count,
            solved_count=history.solved_count,
            failed_count=history.failed_count,
            best_time_ms=history.best_time_ms,
            last_seen_at=history.last_seen_at,
            last_solved_at=history.last_solved_at,
        )
        for history, problem in rows
    ]


@router.get("/{username}", response_model=ProfileOut)
async def public_profile(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    stats = await _get_or_create_stats(db, user)
    return ProfileOut(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        avatar_url=user.avatar_url,
        stats=stats,
    )


async def _get_or_create_stats(db: AsyncSession, user: User) -> UserStats:
    stats = await db.get(UserStats, user.id)
    if stats:
        return stats
    stats = UserStats(user_id=user.id, rating=user.rating or 1200, xp=user.xp or 0)
    db.add(stats)
    await db.commit()
    await db.refresh(stats)
    return stats
