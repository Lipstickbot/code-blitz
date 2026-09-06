from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Match, MatchParticipant, RatingEvent, User, UserStats


K_FACTOR = 32
MIN_RATING = 100


@dataclass
class MatchScore:
    participant: MatchParticipant
    actual_score: float


def expected_score(rating: int, opponent_rating: int) -> float:
    return 1 / (1 + 10 ** ((opponent_rating - rating) / 400))


def calculate_rating(old_rating: int, opponent_rating: int, actual_score: float) -> int:
    expected = expected_score(old_rating, opponent_rating)
    return max(MIN_RATING, round(old_rating + K_FACTOR * (actual_score - expected)))


async def finalize_match_rating(db: AsyncSession, match: Match) -> None:
    """Update ratings once for a finished online match."""
    if match.status != "finished" or match.mode != "online":
        return

    result = await db.execute(
        select(MatchParticipant).where(MatchParticipant.match_id == match.id)
    )
    participants = [participant for participant in result.scalars().all() if participant.user_id]
    if len(participants) != 2:
        return
    if all(participant.rating_after is not None for participant in participants):
        return

    scores = _score_participants(participants, match.winner_user_id)
    left, right = scores
    left_rating = left.participant.rating_before or 1200
    right_rating = right.participant.rating_before or 1200

    await _apply_rating(db, left.participant, left_rating, right_rating, left.actual_score, match.id)
    await _apply_rating(db, right.participant, right_rating, left_rating, right.actual_score, match.id)


def _score_participants(participants: list[MatchParticipant], winner_user_id: str | None) -> list[MatchScore]:
    left, right = participants
    if winner_user_id:
        return [
            MatchScore(left, 1 if left.user_id == winner_user_id else 0),
            MatchScore(right, 1 if right.user_id == winner_user_id else 0),
        ]

    if left.solved_count > right.solved_count:
        return [MatchScore(left, 1), MatchScore(right, 0)]
    if left.solved_count < right.solved_count:
        return [MatchScore(left, 0), MatchScore(right, 1)]

    left_time = left.total_accepted_time_ms or 0
    right_time = right.total_accepted_time_ms or 0
    if left_time and right_time and left_time < right_time:
        return [MatchScore(left, 1), MatchScore(right, 0)]
    if left_time and right_time and right_time < left_time:
        return [MatchScore(left, 0), MatchScore(right, 1)]

    return [MatchScore(left, 0.5), MatchScore(right, 0.5)]


async def _apply_rating(
    db: AsyncSession,
    participant: MatchParticipant,
    old_rating: int,
    opponent_rating: int,
    actual_score: float,
    match_id: str,
) -> None:
    new_rating = calculate_rating(old_rating, opponent_rating, actual_score)
    participant.rating_after = new_rating

    user = await db.get(User, participant.user_id)
    stats = await db.get(UserStats, participant.user_id)
    if not stats:
        stats = UserStats(user_id=participant.user_id, rating=old_rating)
        db.add(stats)

    stats.rating = new_rating
    stats.games_played += 1
    if actual_score == 1:
        stats.wins += 1
    elif actual_score == 0:
        stats.losses += 1
    else:
        stats.draws += 1

    if user:
        user.rating = new_rating

    db.add(
        RatingEvent(
            user_id=participant.user_id,
            match_id=match_id,
            rating_before=old_rating,
            rating_after=new_rating,
            reason="ranked_match",
        )
    )
