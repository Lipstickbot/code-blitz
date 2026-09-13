from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Tournament, TournamentBracketMatch, TournamentParticipant, TournamentRound, User
from app.schemas import TournamentBracketMatchOut, TournamentCreateIn, TournamentOut, TournamentParticipantOut
from app.services.rate_limiter import matchmaking_rate_limiter
from app.services.tournaments import create_tournament, get_tournament_for_user, list_my_tournaments


router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.post("", response_model=TournamentOut)
async def create_tournament_room(
    payload: TournamentCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "create")
    tournament = await create_tournament(db, current_user, payload.name, payload.player_usernames)
    return await _tournament_out(db, tournament)


@router.get("", response_model=list[TournamentOut])
async def my_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "list")
    tournaments = await list_my_tournaments(db, current_user)
    return [await _tournament_out(db, tournament) for tournament in tournaments]


@router.get("/{tournament_id}", response_model=TournamentOut)
async def tournament_detail(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "detail")
    tournament = await get_tournament_for_user(db, tournament_id, current_user)
    return await _tournament_out(db, tournament)


@router.get("/{tournament_id}/bracket", response_model=TournamentOut)
async def tournament_bracket(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "bracket")
    tournament = await get_tournament_for_user(db, tournament_id, current_user)
    return await _tournament_out(db, tournament)


def _check_tournament_rate_limit(user: User, action: str) -> None:
    result = matchmaking_rate_limiter.check(
        f"tournament:{action}:user:{user.id}",
        limit=settings.matchmaking_rate_limit_count,
        window_seconds=settings.matchmaking_rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many tournament requests. Try again in {result.retry_after_seconds} seconds.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )


async def _tournament_out(db: AsyncSession, tournament: Tournament) -> TournamentOut:
    participant_rows = await db.execute(
        select(TournamentParticipant, User.username)
        .join(User, User.id == TournamentParticipant.user_id)
        .where(TournamentParticipant.tournament_id == tournament.id)
        .order_by(TournamentParticipant.seed)
    )
    participants = [
        TournamentParticipantOut(
            id=participant.id,
            user_id=participant.user_id,
            username=username,
            seed=participant.seed,
            status=participant.status,
            eliminated_round=participant.eliminated_round,
        )
        for participant, username in participant_rows.all()
    ]
    username_by_participant_id = {participant.id: participant.username for participant in participants}

    bracket_rows = await db.execute(
        select(TournamentBracketMatch, TournamentRound.round_number)
        .join(TournamentRound, TournamentRound.id == TournamentBracketMatch.round_id)
        .where(TournamentBracketMatch.tournament_id == tournament.id)
        .order_by(TournamentRound.round_number, TournamentBracketMatch.bracket_position)
    )
    bracket = [
        TournamentBracketMatchOut(
            id=bracket_match.id,
            round_number=round_number,
            bracket_position=bracket_match.bracket_position,
            match_id=bracket_match.match_id,
            status=bracket_match.status,
            left_participant_id=bracket_match.left_participant_id,
            right_participant_id=bracket_match.right_participant_id,
            left_username=username_by_participant_id.get(bracket_match.left_participant_id),
            right_username=username_by_participant_id.get(bracket_match.right_participant_id),
            winner_participant_id=bracket_match.winner_participant_id,
            loser_participant_id=bracket_match.loser_participant_id,
            next_bracket_match_id=bracket_match.next_bracket_match_id,
            next_slot=bracket_match.next_slot,
        )
        for bracket_match, round_number in bracket_rows.all()
    ]

    return TournamentOut(
        id=tournament.id,
        name=tournament.name,
        status=tournament.status,
        creator_user_id=tournament.creator_user_id,
        player_count=tournament.player_count,
        max_players=tournament.max_players,
        champion_user_id=tournament.champion_user_id,
        created_at=tournament.created_at,
        started_at=tournament.started_at,
        finished_at=tournament.finished_at,
        participants=participants,
        bracket=bracket,
    )
