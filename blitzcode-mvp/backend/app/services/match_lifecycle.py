from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Match, MatchEvent, MatchParticipant
from app.services import rating
from app.services.match_hub import match_hub


async def finish_match(
    db: AsyncSession,
    match: Match,
    reason: str,
    winner_user_id: str | None = None,
    metadata: dict | None = None,
) -> Match:
    """Finish a match once and apply all side effects in one place."""
    if match.status == "finished":
        return match

    participants = await _get_participants(db, match.id)
    now = datetime.utcnow()
    winner_id = winner_user_id if winner_user_id is not None else _pick_winner(participants)

    match.status = "finished"
    match.finished_at = now
    match.winner_user_id = winner_id

    for participant in participants:
        if participant.user_id == winner_id and not participant.finished_at:
            participant.finished_at = now

    await rating.finalize_match_rating(db, match)
    if match.mode == "tournament":
        from app.services.tournaments import advance_tournament_after_match

        await advance_tournament_after_match(db, match)

    event_payload = {
        "reason": reason,
        "winner_user_id": winner_id,
        **(metadata or {}),
        "participants": [
            {
                "user_id": participant.user_id,
                "side": participant.side,
                "solved_count": participant.solved_count,
                "progress_percent": float(participant.progress_percent),
                "total_accepted_time_ms": participant.total_accepted_time_ms,
                "rating_before": participant.rating_before,
                "rating_after": participant.rating_after,
            }
            for participant in participants
        ],
    }
    db.add(
        MatchEvent(
            match_id=match.id,
            user_id=winner_id,
            type="match_finished",
            payload=event_payload,
        )
    )
    await match_hub.broadcast(
        match.id,
        {
            "type": "match_finished",
            "match_id": match.id,
            "user_id": winner_id,
            "payload": event_payload,
        },
    )
    return match


async def finish_match_if_expired(db: AsyncSession, match: Match) -> bool:
    if match.status == "finished" or not match.started_at:
        return False

    deadline = match.started_at + timedelta(seconds=match.duration_seconds)
    if datetime.utcnow() <= deadline:
        return False

    await finish_match(db, match, reason="time_expired")
    return True


async def _get_participants(db: AsyncSession, match_id: str) -> list[MatchParticipant]:
    result = await db.execute(
        select(MatchParticipant)
        .where(MatchParticipant.match_id == match_id)
        .order_by(MatchParticipant.side)
    )
    return list(result.scalars().all())


def _pick_winner(participants: list[MatchParticipant]) -> str | None:
    players = [participant for participant in participants if participant.user_id]
    if len(players) != 2:
        return None

    left, right = players
    if left.solved_count > right.solved_count:
        return left.user_id
    if right.solved_count > left.solved_count:
        return right.user_id

    left_time = left.total_accepted_time_ms or 0
    right_time = right.total_accepted_time_ms or 0
    if left_time and right_time and left_time < right_time:
        return left.user_id
    if left_time and right_time and right_time < left_time:
        return right.user_id

    return None
