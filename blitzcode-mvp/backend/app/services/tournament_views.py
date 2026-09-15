from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tournament, TournamentBracketMatch, TournamentParticipant, TournamentRound, User
from app.schemas import (
    TournamentBracketMatchOut,
    TournamentOut,
    TournamentParticipantOut,
    TournamentRoundOut,
)


async def tournament_out(db: AsyncSession, tournament: Tournament) -> TournamentOut:
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
        select(TournamentBracketMatch, TournamentRound.round_number, TournamentRound.name, TournamentRound.status)
        .join(TournamentRound, TournamentRound.id == TournamentBracketMatch.round_id)
        .where(TournamentBracketMatch.tournament_id == tournament.id)
        .order_by(TournamentRound.round_number, TournamentBracketMatch.bracket_position)
    )
    bracket = [
        TournamentBracketMatchOut(
            id=bracket_match.id,
            round_number=round_number,
            round_name=round_name,
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
        for bracket_match, round_number, round_name, _round_status in bracket_rows.all()
    ]
    round_rows = await db.execute(
        select(TournamentRound)
        .where(TournamentRound.tournament_id == tournament.id)
        .order_by(TournamentRound.round_number)
    )
    rounds = [
        TournamentRoundOut(
            round_number=round_row.round_number,
            name=round_row.name,
            status=round_row.status,
            match_count=sum(1 for bracket_match in bracket if bracket_match.round_number == round_row.round_number),
            matches=[bracket_match for bracket_match in bracket if bracket_match.round_number == round_row.round_number],
        )
        for round_row in round_rows.scalars().all()
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
        rounds=rounds,
        bracket=bracket,
    )
