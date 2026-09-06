from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_optional
from app.config import settings
from app.database import get_db
from app.models import (
    BlitzSession,
    BlitzSessionProblem,
    Match,
    MatchEvent,
    MatchParticipant,
    MatchTask,
    Problem,
    Submission,
    SubmissionCaseResult,
    TestCase,
    User,
)
from app.schemas import SubmissionIn, SubmissionOut
from app.services import judge, scoring
from app.services.anti_cheat import record_submission_signals
from app.services.match_hub import match_hub
from app.services.match_lifecycle import finish_match, finish_match_if_expired
from app.services.rate_limiter import submission_rate_limiter


router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut)
async def create_submission(
    request: Request,
    payload: SubmissionIn,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    problem = await _get_problem(db, payload.problem_id)
    if payload.kind not in {"run", "submit"}:
        raise HTTPException(status_code=400, detail="kind must be run or submit")
    if payload.match_id and not current_user:
        raise HTTPException(status_code=401, detail="Login is required for match submissions")
    _validate_submission_size(payload.code)
    _check_submission_rate_limit(request, current_user)

    await _reject_expired_legacy_blitz(db, payload.blitz_session_id)
    await _reject_expired_match(db, payload.match_id)
    await _validate_match_submission(db, payload, current_user)

    test_cases = await _select_test_cases(db, problem.id, payload.kind)
    if not test_cases:
        raise HTTPException(status_code=503, detail="No test cases available for this problem")

    judge_result = judge.evaluate(
        payload.code,
        payload.language,
        test_cases,
        timeout_seconds=_judge_timeout_seconds(problem),
    )

    submission = Submission(
        user_id=current_user.id if current_user else None,
        problem_id=problem.id,
        match_id=payload.match_id,
        match_task_id=payload.match_task_id,
        kind=payload.kind,
        language=payload.language,
        code=payload.code,
        status=judge_result.status,
        execution_time_ms=judge_result.runtime_ms,
        runtime_ms=judge_result.runtime_ms,
        passed_count=judge_result.passed_count,
        total_count=judge_result.total_count,
        error_message=judge_result.error_message,
        blitz_session_id=payload.blitz_session_id,
    )
    db.add(submission)
    await db.flush()

    db.add_all(
        [
            SubmissionCaseResult(
                submission_id=submission.id,
                test_case_id=item.test_case_id,
                position=item.position,
                status=item.status,
                actual_json=item.actual,
                expected_json=item.expected,
                runtime_ms=item.runtime_ms,
                error_message=item.error_message,
            )
            for item in judge_result.case_results
        ]
    )

    match_started_at = await _get_match_started_at(db, payload.match_id)
    await record_submission_signals(
        db,
        submission=submission,
        problem=problem,
        match_started_at=match_started_at,
    )

    if payload.kind == "submit" and judge_result.status == "accepted" and current_user:
        await scoring.record_problem_result(db, current_user, problem, accepted=True)
        await _mark_online_match_progress(db, payload, current_user)
        await _mark_legacy_blitz_progress(db, payload, current_user, problem)
    elif payload.kind == "submit" and current_user:
        await scoring.record_problem_result(db, current_user, problem, accepted=False)

    await db.commit()

    return SubmissionOut(
        status=judge_result.status,
        execution_time_ms=judge_result.runtime_ms,
        message=judge_result.error_message,
        passed_count=judge_result.passed_count,
        total_count=judge_result.total_count,
        case_results=[
            {
                "position": item.position,
                "status": item.status,
                "actual": item.actual,
                "expected": item.expected,
                "runtime_ms": item.runtime_ms,
                "error_message": item.error_message,
            }
            for item in judge_result.case_results
        ],
    )


async def _get_problem(db: AsyncSession, problem_id: str) -> Problem:
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


def _validate_submission_size(code: str) -> None:
    size = len(code.encode("utf-8"))
    if size > settings.max_submission_code_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Code is too large. Limit is {settings.max_submission_code_bytes} bytes.",
        )


def _check_submission_rate_limit(request: Request, user: User | None) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"user:{user.id}" if user else f"ip:{client_host}"
    result = submission_rate_limiter.check(
        key,
        limit=settings.submission_rate_limit_count,
        window_seconds=settings.submission_rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many submissions. Try again in {result.retry_after_seconds} seconds.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )


def _judge_timeout_seconds(problem: Problem) -> float:
    configured = (problem.time_limit_ms or 1000) / 1000
    return max(
        settings.min_judge_timeout_seconds,
        min(settings.max_judge_timeout_seconds, configured),
    )


async def _select_test_cases(db: AsyncSession, problem_id: str, kind: str) -> list[TestCase]:
    query = select(TestCase).where(TestCase.problem_id == problem_id)
    if kind == "run":
        query = (
            query.where(TestCase.is_sample == True)  # noqa: E712
            .order_by(TestCase.position)
            .limit(settings.run_test_limit)
        )
    else:
        query = (
            query.where(TestCase.is_hidden == True)  # noqa: E712
            .order_by(TestCase.position)
            .limit(settings.submit_test_limit)
        )
    result = await db.execute(query)
    test_cases = list(result.scalars().all())
    if test_cases:
        return test_cases

    fallback = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .order_by(TestCase.position)
        .limit(settings.run_test_limit if kind == "run" else settings.submit_test_limit)
    )
    return list(fallback.scalars().all())


async def _reject_expired_legacy_blitz(db: AsyncSession, blitz_session_id: str | None) -> None:
    if not blitz_session_id:
        return
    result = await db.execute(select(BlitzSession).where(BlitzSession.id == blitz_session_id))
    blitz_session = result.scalar_one_or_none()
    if not blitz_session:
        return
    deadline = blitz_session.started_at + timedelta(minutes=blitz_session.duration_minutes)
    if datetime.utcnow() > deadline:
        raise HTTPException(status_code=400, detail="Blitz session time is up")


async def _reject_expired_match(db: AsyncSession, match_id: str | None) -> None:
    if not match_id:
        return
    match = await db.get(Match, match_id)
    if not match or not match.started_at:
        return
    if match.status == "finished":
        raise HTTPException(status_code=400, detail="Match already finished")
    if await finish_match_if_expired(db, match):
        await db.commit()
        raise HTTPException(status_code=400, detail="Match time is up")


async def _get_match_started_at(db: AsyncSession, match_id: str | None) -> datetime | None:
    if not match_id:
        return None
    match = await db.get(Match, match_id)
    return match.started_at if match else None


async def _validate_match_submission(
    db: AsyncSession,
    payload: SubmissionIn,
    user: User | None,
) -> None:
    if not payload.match_id and not payload.match_task_id:
        return
    if not payload.match_id or not payload.match_task_id:
        raise HTTPException(status_code=400, detail="match_id and match_task_id must be provided together")
    if not user:
        raise HTTPException(status_code=401, detail="Login is required for match submissions")

    participant = await _get_match_participant(db, payload.match_id, user.id)
    task = await _get_match_task(db, payload.match_id, payload.match_task_id)
    if task.problem_id != payload.problem_id:
        raise HTTPException(status_code=400, detail="Submitted problem does not match match task")

    if payload.kind != "submit":
        return

    if participant.side == "left" and task.accepted_by_left_at:
        raise HTTPException(status_code=400, detail="Match task already accepted")
    if participant.side == "right" and task.accepted_by_right_at:
        raise HTTPException(status_code=400, detail="Match task already accepted")


async def _get_match_participant(db: AsyncSession, match_id: str, user_id: str) -> MatchParticipant:
    result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == user_id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Match participant not found")
    return participant


async def _get_match_task(db: AsyncSession, match_id: str, match_task_id: str) -> MatchTask:
    task = await db.get(MatchTask, match_task_id)
    if not task or task.match_id != match_id:
        raise HTTPException(status_code=404, detail="Match task not found")
    return task


async def _mark_online_match_progress(db: AsyncSession, payload: SubmissionIn, user: User) -> None:
    if not payload.match_id or not payload.match_task_id:
        return

    participant = await _get_match_participant(db, payload.match_id, user.id)
    task = await _get_match_task(db, payload.match_id, payload.match_task_id)

    now = datetime.utcnow()
    accepted_time_ms = 0
    match = await db.get(Match, payload.match_id)
    if match and match.started_at:
        accepted_time_ms = max(0, int((now - match.started_at).total_seconds() * 1000))

    accepted_new_task = False
    if participant.side == "left" and not task.accepted_by_left_at:
        task.accepted_by_left_at = now
        participant.solved_count += 1
        participant.total_accepted_time_ms += accepted_time_ms
        accepted_new_task = True
    elif participant.side == "right" and not task.accepted_by_right_at:
        task.accepted_by_right_at = now
        participant.solved_count += 1
        participant.total_accepted_time_ms += accepted_time_ms
        accepted_new_task = True

    if not accepted_new_task:
        return

    task_count_result = await db.execute(select(MatchTask).where(MatchTask.match_id == payload.match_id))
    task_count = len(task_count_result.scalars().all()) or 1
    participant.progress_percent = round((participant.solved_count / task_count) * 100, 2)

    accepted_payload = {
        "problem_id": payload.problem_id,
        "solved_count": participant.solved_count,
        "progress_percent": float(participant.progress_percent),
    }
    db.add(
        MatchEvent(
            match_id=payload.match_id,
            user_id=user.id,
            match_task_id=payload.match_task_id,
            type="task_accepted",
            payload=accepted_payload,
        )
    )
    await match_hub.broadcast(
        payload.match_id,
        {
            "type": "task_accepted",
            "match_id": payload.match_id,
            "user_id": user.id,
            "match_task_id": payload.match_task_id,
            "payload": accepted_payload,
        },
    )

    if match and participant.solved_count >= task_count:
        participant.finished_at = now
        await finish_match(db, match, reason="all_tasks_solved", winner_user_id=user.id)


async def _mark_legacy_blitz_progress(
    db: AsyncSession,
    payload: SubmissionIn,
    current_user: User,
    problem: Problem,
) -> None:
    if not payload.blitz_session_id:
        return
    result = await db.execute(
        select(BlitzSessionProblem).where(
            BlitzSessionProblem.blitz_session_id == payload.blitz_session_id,
            BlitzSessionProblem.problem_id == problem.id,
        )
    )
    session_problem = result.scalar_one_or_none()
    if not session_problem or session_problem.solved:
        return

    points = scoring.award_blitz_points(current_user, problem.difficulty)
    session_problem.solved = True
    session_problem.points_earned = points

    blitz_result = await db.execute(select(BlitzSession).where(BlitzSession.id == payload.blitz_session_id))
    blitz_session = blitz_result.scalar_one_or_none()
    if blitz_session:
        blitz_session.total_score += points
        blitz_session.problems_solved_count += 1
