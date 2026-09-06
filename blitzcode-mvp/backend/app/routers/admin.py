from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import AntiCheatSignal, Problem, Submission, User
from app.schemas import AntiCheatSignalOut, ProblemCalibrationOut


router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/problem-calibration", response_model=list[ProblemCalibrationOut])
async def list_problem_calibration(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    attempts_expr = func.count(Submission.id)
    accepted_expr = func.sum(case((Submission.status == "accepted", 1), else_=0))
    runtime_expr = func.avg(Submission.runtime_ms)
    result = await db.execute(
        select(
            Problem.id,
            Problem.title,
            Problem.difficulty,
            attempts_expr.label("attempts"),
            accepted_expr.label("accepted"),
            runtime_expr.label("average_runtime_ms"),
        )
        .outerjoin(Submission, Submission.problem_id == Problem.id)
        .where(Problem.status == "active")
        .group_by(Problem.id, Problem.title, Problem.difficulty)
        .order_by(desc(attempts_expr), Problem.title)
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    return [
        ProblemCalibrationOut(
            problem_id=problem_id,
            title=title,
            difficulty=difficulty,
            attempts=int(attempts or 0),
            accepted=int(accepted or 0),
            acceptance_rate=_acceptance_rate(attempts, accepted),
            average_runtime_ms=int(average_runtime_ms) if average_runtime_ms is not None else None,
            recommendation=_calibration_recommendation(difficulty, attempts, accepted),
        )
        for problem_id, title, difficulty, attempts, accepted, average_runtime_ms in rows
    ]


def _acceptance_rate(attempts: int | None, accepted: int | None) -> float:
    if not attempts:
        return 0.0
    return round((int(accepted or 0) / int(attempts)) * 100, 1)


def _calibration_recommendation(difficulty: str, attempts: int | None, accepted: int | None) -> str:
    if not attempts or attempts < 10:
        return "need more data"
    rate = _acceptance_rate(attempts, accepted)
    if difficulty == "easy" and rate < 35:
        return "review: may be too hard for easy"
    if difficulty == "medium" and rate > 78:
        return "review: may be too easy for medium"
    if difficulty == "hard" and rate > 55:
        return "review: may be too easy for hard"
    if rate < 18:
        return "review statement/tests"
    return "looks balanced"


@router.get("/anti-cheat/signals", response_model=list[AntiCheatSignalOut])
async def list_anti_cheat_signals(
    reviewed: bool | None = None,
    severity: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    query = (
        select(AntiCheatSignal, User.username, Problem.title)
        .outerjoin(User, User.id == AntiCheatSignal.user_id)
        .outerjoin(Problem, Problem.id == AntiCheatSignal.problem_id)
    )
    if reviewed is not None:
        query = query.where(AntiCheatSignal.reviewed == reviewed)
    if severity:
        query = query.where(AntiCheatSignal.severity == severity)
    result = await db.execute(
        query.order_by(desc(AntiCheatSignal.created_at))
        .offset(offset)
        .limit(limit)
    )
    return [
        AntiCheatSignalOut(
            id=signal.id,
            user_id=signal.user_id,
            username=username,
            submission_id=signal.submission_id,
            match_id=signal.match_id,
            problem_id=signal.problem_id,
            problem_title=problem_title,
            signal_type=signal.signal_type,
            severity=signal.severity,
            payload=signal.payload,
            reviewed=signal.reviewed,
            created_at=signal.created_at,
        )
        for signal, username, problem_title in result.all()
    ]


@router.patch("/anti-cheat/signals/{signal_id}/reviewed", response_model=AntiCheatSignalOut)
async def mark_anti_cheat_signal_reviewed(
    signal_id: str,
    reviewed: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    signal = await db.get(AntiCheatSignal, signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Anti-cheat signal not found")
    signal.reviewed = reviewed
    await db.commit()
    await db.refresh(signal)

    username = None
    problem_title = None
    if signal.user_id:
        user = await db.get(User, signal.user_id)
        username = user.username if user else None
    if signal.problem_id:
        problem = await db.get(Problem, signal.problem_id)
        problem_title = problem.title if problem else None

    return AntiCheatSignalOut(
        id=signal.id,
        user_id=signal.user_id,
        username=username,
        submission_id=signal.submission_id,
        match_id=signal.match_id,
        problem_id=signal.problem_id,
        problem_title=problem_title,
        signal_type=signal.signal_type,
        severity=signal.severity,
        payload=signal.payload,
        reviewed=signal.reviewed,
        created_at=signal.created_at,
    )
