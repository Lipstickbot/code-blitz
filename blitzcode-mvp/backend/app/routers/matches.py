from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user, get_user_from_token
from app.database import get_db
from app.models import Match, MatchEvent, MatchParticipant, MatchTask, Problem, Submission, TestCase, User
from app.schemas import (
    MatchEventOut,
    MatchFinishResponse,
    MatchOut,
    MatchReplayOut,
    MatchReplaySubmissionOut,
    MatchReplayTaskOut,
    MatchTaskProblemOut,
)
from app.services.match_hub import match_hub
from app.services.match_lifecycle import finish_match, finish_match_if_expired
from app.services.matchmaker import get_active_match_for_user
from app.services.bot_match import advance_bot_match
from app.services.past_self_match import advance_past_self_match


router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/active", response_model=MatchOut | None)
async def get_active_match(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = await get_active_match_for_user(db, current_user.id)
    if not match:
        return None
    if await _advance_automated_opponent(db, match):
        await db.commit()
    return match


@router.get("/{match_id}", response_model=MatchOut)
async def get_match(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.participants), selectinload(Match.tasks))
        .join(MatchParticipant)
        .where(Match.id == match_id, MatchParticipant.user_id == current_user.id)
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if await finish_match_if_expired(db, match):
        await db.commit()
    elif await _advance_automated_opponent(db, match):
        await db.commit()
    return match


@router.get("/{match_id}/tasks", response_model=list[MatchTaskProblemOut])
async def get_match_tasks(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _require_match_participant(db, match_id, current_user.id)
    match = await db.get(Match, match_id)
    if match and await _advance_automated_opponent(db, match):
        await db.commit()
    result = await db.execute(
        select(MatchTask, Problem)
        .join(Problem, Problem.id == MatchTask.problem_id)
        .where(MatchTask.match_id == match_id)
        .order_by(MatchTask.position)
    )
    rows = result.all()
    payload: list[MatchTaskProblemOut] = []
    for task, problem in rows:
        samples = await _sample_tests(db, problem.id)
        payload.append(
            MatchTaskProblemOut(
                match_task_id=task.id,
                position=task.position,
                problem_id=problem.id,
                slug=problem.slug,
                title=problem.title,
                statement=problem.statement,
                description=problem.description,
                difficulty=problem.difficulty,
                tags=problem.tags,
                starter_code_js=problem.starter_code_js,
                time_limit_ms=problem.time_limit_ms,
                sample_tests=samples,
            )
        )
    return payload


@router.get("/{match_id}/replay", response_model=MatchReplayOut)
async def get_match_replay(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _require_match_participant(db, match_id, current_user.id)
    match_result = await db.execute(
        select(Match)
        .options(selectinload(Match.participants), selectinload(Match.tasks))
        .where(Match.id == match_id)
    )
    match = match_result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if await finish_match_if_expired(db, match):
        await db.commit()
    elif await _advance_automated_opponent(db, match):
        await db.commit()

    task_rows = (
        await db.execute(
            select(MatchTask, Problem)
            .join(Problem, Problem.id == MatchTask.problem_id)
            .where(MatchTask.match_id == match_id)
            .order_by(MatchTask.position)
        )
    ).all()
    event_rows = (
        await db.execute(
            select(MatchEvent)
            .where(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.created_at)
        )
    ).scalars().all()
    submission_rows = (
        await db.execute(
            select(Submission)
            .where(Submission.match_id == match_id)
            .order_by(Submission.created_at)
        )
    ).scalars().all()

    return MatchReplayOut(
        match=match,
        tasks=[
            MatchReplayTaskOut(
                match_task_id=task.id,
                position=task.position,
                problem_id=problem.id,
                title=problem.title,
                difficulty=problem.difficulty,
                accepted_by_left_at=task.accepted_by_left_at,
                accepted_by_right_at=task.accepted_by_right_at,
            )
            for task, problem in task_rows
        ],
        events=list(event_rows),
        submissions=[
            MatchReplaySubmissionOut(
                id=submission.id,
                user_id=submission.user_id,
                problem_id=submission.problem_id,
                match_task_id=submission.match_task_id,
                kind=submission.kind,
                language=submission.language,
                status=submission.status,
                passed_count=submission.passed_count,
                total_count=submission.total_count,
                runtime_ms=submission.runtime_ms,
                created_at=submission.created_at,
            )
            for submission in submission_rows
        ],
    )


@router.post("/{match_id}/finish", response_model=MatchFinishResponse)
async def finish_match_endpoint(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _require_match_participant(db, match_id, current_user.id)
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    finished = await finish_match(db, match, reason="manual_finish")
    await db.commit()
    return MatchFinishResponse(
        match_id=finished.id,
        status=finished.status,
        winner_user_id=finished.winner_user_id,
        finished_at=finished.finished_at,
    )


@router.post("/{match_id}/forfeit", response_model=MatchFinishResponse)
async def forfeit_match_endpoint(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    participant = await _require_match_participant(db, match_id, current_user.id)
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status == "finished":
        raise HTTPException(status_code=400, detail="Match already finished")

    opponent_result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id != participant.user_id,
        )
    )
    opponent = opponent_result.scalar_one_or_none()
    winner_id = opponent.user_id if opponent and opponent.user_id else None

    finished = await finish_match(
        db,
        match,
        reason="forfeit",
        winner_user_id=winner_id,
        metadata={"forfeited_user_id": current_user.id},
    )
    await db.commit()
    return MatchFinishResponse(
        match_id=finished.id,
        status=finished.status,
        winner_user_id=finished.winner_user_id,
        finished_at=finished.finished_at,
    )


@router.get("/{match_id}/events", response_model=list[MatchEventOut])
async def get_match_events(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _require_match_participant(db, match_id, current_user.id)

    result = await db.execute(
        select(MatchEvent)
        .where(MatchEvent.match_id == match_id)
        .order_by(MatchEvent.created_at)
    )
    return list(result.scalars().all())


@router.websocket("/{match_id}/stream")
async def stream_match(match_id: str, websocket: WebSocket, token: str | None = None):
    async for db in get_db():
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=4401)
            return

        participant_result = await db.execute(
            select(MatchParticipant).where(
                MatchParticipant.match_id == match_id,
                MatchParticipant.user_id == user.id,
            )
        )
        if not participant_result.scalar_one_or_none():
            await websocket.close(code=4404)
            return

        match_result = await db.execute(
            select(Match)
            .options(selectinload(Match.participants), selectinload(Match.tasks))
            .where(Match.id == match_id)
        )
        match = match_result.scalar_one_or_none()
        if not match:
            await websocket.close(code=4404)
            return

        await match_hub.connect(match_id, websocket)
        await websocket.send_json(
            {
                "type": "snapshot",
                "match_id": match.id,
                "status": match.status,
                "participants": [
                    {
                        "user_id": item.user_id,
                        "side": item.side,
                        "display_name": item.display_name,
                        "solved_count": item.solved_count,
                        "progress_percent": float(item.progress_percent),
                        "rating_before": item.rating_before,
                        "rating_after": item.rating_after,
                    }
                    for item in match.participants
                ],
                "tasks": [
                    {
                        "id": item.id,
                        "problem_id": item.problem_id,
                        "position": item.position,
                        "difficulty": item.difficulty,
                    }
                    for item in match.tasks
                ],
            }
        )

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            match_hub.disconnect(match_id, websocket)
        return


async def _require_match_participant(db: AsyncSession, match_id: str, user_id: str) -> MatchParticipant:
    result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == user_id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Match not found")
    return participant


async def _sample_tests(db: AsyncSession, problem_id: str) -> list[dict]:
    result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id, TestCase.is_sample == True)  # noqa: E712
        .order_by(TestCase.position)
        .limit(5)
    )
    samples = list(result.scalars().all())
    return [
        {
            "position": test.position,
            "input": test.input_json if test.input_json is not None else test.input,
            "expected": test.expected_json if test.expected_json is not None else test.expected_output,
            "explanation": test.explanation,
        }
        for test in samples
    ]


async def _advance_automated_opponent(db: AsyncSession, match: Match) -> bool:
    if match.mode == "bot":
        return await advance_bot_match(db, match)
    if match.mode == "past_self":
        return await advance_past_self_match(db, match)
    return False
