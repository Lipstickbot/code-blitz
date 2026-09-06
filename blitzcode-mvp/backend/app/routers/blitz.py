import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import BlitzSession, BlitzSessionProblem, Problem, User
from app.schemas import BlitzStartRequest, BlitzStartResponse, BlitzFinishResponse

router = APIRouter(prefix="/api/blitz", tags=["blitz"])

ALLOWED_DURATIONS = {5, 10, 15}
POOL_SIZE_BY_DURATION = {5: 4, 10: 8, 15: 12}
DIFFICULTY_ORDER = ["easy", "easy", "medium", "medium", "hard"]


@router.post("/start", response_model=BlitzStartResponse)
async def start_session(
    payload: BlitzStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.duration_minutes not in ALLOWED_DURATIONS:
        raise HTTPException(status_code=400, detail="duration_minutes must be 5, 10 or 15")

    pool_size = POOL_SIZE_BY_DURATION[payload.duration_minutes]

    # Build a pool of increasing difficulty. Falls back to whatever is
    # available if the bank doesn't have enough problems yet.
    all_problems = (await db.execute(select(Problem))).scalars().all()
    if not all_problems:
        raise HTTPException(status_code=503, detail="No problems available yet")

    by_difficulty: dict[str, list[Problem]] = {"easy": [], "medium": [], "hard": []}
    for p in all_problems:
        by_difficulty.setdefault(p.difficulty, []).append(p)

    chosen: list[Problem] = []
    for i in range(pool_size):
        difficulty = DIFFICULTY_ORDER[min(i, len(DIFFICULTY_ORDER) - 1)]
        candidates = by_difficulty.get(difficulty) or all_problems
        chosen.append(random.choice(candidates))

    session = BlitzSession(
        user_id=current_user.id,
        duration_minutes=payload.duration_minutes,
        started_at=datetime.utcnow(),
        status="in_progress",
    )
    session.session_problems = [
        BlitzSessionProblem(problem_id=p.id, order_index=i) for i, p in enumerate(chosen)
    ]
    db.add(session)
    await db.commit()
    await db.refresh(session)

    ends_at = session.started_at + timedelta(minutes=payload.duration_minutes)

    return BlitzStartResponse(
        session_id=session.id,
        ends_at=ends_at,
        problem_ids=[p.id for p in chosen],
    )


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(BlitzSession).where(BlitzSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    ends_at = session.started_at + timedelta(minutes=session.duration_minutes)
    is_expired = datetime.utcnow() > ends_at

    return {
        "session_id": session.id,
        "status": "finished" if is_expired else session.status,
        "ends_at": ends_at,
        "total_score": session.total_score,
        "problems_solved_count": session.problems_solved_count,
    }


@router.post("/session/{session_id}/finish", response_model=BlitzFinishResponse)
async def finish_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(BlitzSession).where(BlitzSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "finished"
    session.finished_at = datetime.utcnow()
    await db.commit()

    return BlitzFinishResponse(
        total_score=session.total_score,
        problems_solved_count=session.problems_solved_count,
        duration_minutes=session.duration_minutes,
    )
