from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Match,
    MatchParticipant,
    MatchTask,
    MatchmakingQueue,
    Tournament,
    TournamentBracketMatch,
    TournamentParticipant,
    TournamentRound,
    User,
    UserStats,
)
from app.services.matchmaker import MATCH_DURATION_SECONDS
from app.services.task_picker import pick_ranked_match_tasks
from app.services.tournament_hub import tournament_hub
from app.services.tournament_rules import (
    MAX_TOURNAMENT_PLAYERS,
    first_round_seed_pairs,
    is_valid_tournament_size,
    tournament_round_count,
    tournament_round_name,
)


async def create_tournament(
    db: AsyncSession,
    creator: User,
    name: str,
    player_usernames: list[str],
) -> Tournament:
    usernames = _normalize_tournament_usernames(creator.username, player_usernames)
    if not is_valid_tournament_size(len(usernames)):
        raise HTTPException(status_code=400, detail="Tournament players must be 2, 4, 8, 16, or 32")

    users = await _load_users_by_usernames(db, usernames)
    await _ensure_players_are_available(db, [user.id for user in users])
    await _cancel_open_searches(db, [user.id for user in users])
    seeded_users = await _seed_users_by_rating(db, users)

    now = datetime.utcnow()
    tournament = Tournament(
        name=name.strip(),
        creator_user_id=creator.id,
        status="active",
        max_players=MAX_TOURNAMENT_PLAYERS,
        player_count=len(seeded_users),
        started_at=now,
    )
    db.add(tournament)
    await db.flush()

    participants = [
        TournamentParticipant(
            tournament_id=tournament.id,
            user_id=user.id,
            seed=index + 1,
            status="active",
        )
        for index, user in enumerate(seeded_users)
    ]
    db.add_all(participants)
    await db.flush()

    rounds, bracket_by_round = await _create_bracket_shell(db, tournament, len(participants))
    first_round = bracket_by_round[1]
    participants_by_seed = {participant.seed: participant for participant in participants}
    for index, (left_seed, right_seed) in enumerate(first_round_seed_pairs(len(participants))):
        bracket_match = first_round[index]
        bracket_match.left_participant_id = participants_by_seed[left_seed].id
        bracket_match.right_participant_id = participants_by_seed[right_seed].id
    await db.flush()

    rounds[0].status = "active"
    for bracket_match in first_round:
        await _create_match_for_bracket(db, bracket_match)

    await db.commit()
    await db.refresh(tournament)
    return tournament


async def list_my_tournaments(db: AsyncSession, user: User) -> list[Tournament]:
    participant_ids = select(TournamentParticipant.tournament_id).where(TournamentParticipant.user_id == user.id)
    result = await db.execute(
        select(Tournament)
        .where(Tournament.id.in_(participant_ids))
        .order_by(Tournament.created_at.desc())
        .limit(25)
    )
    return list(result.scalars().all())


async def list_admin_tournaments(
    db: AsyncSession,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Tournament]:
    query = select(Tournament)
    if status:
        query = query.where(Tournament.status == status)
    query = query.order_by(Tournament.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_tournament_for_user(db: AsyncSession, tournament_id: str, user: User) -> Tournament:
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    result = await db.execute(
        select(TournamentParticipant.id).where(
            TournamentParticipant.tournament_id == tournament_id,
            TournamentParticipant.user_id == user.id,
        )
    )
    if tournament.creator_user_id != user.id and not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


async def cancel_tournament(db: AsyncSession, tournament_id: str) -> Tournament:
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    if tournament.status == "finished":
        raise HTTPException(status_code=400, detail="Finished tournaments cannot be canceled")
    if tournament.status == "cancelled":
        return tournament

    now = datetime.utcnow()
    tournament.status = "cancelled"
    tournament.finished_at = now

    participant_result = await db.execute(
        select(TournamentParticipant).where(TournamentParticipant.tournament_id == tournament_id)
    )
    for participant in participant_result.scalars().all():
        if participant.status == "active":
            participant.status = "cancelled"
            participant.eliminated_at = now

    round_result = await db.execute(select(TournamentRound).where(TournamentRound.tournament_id == tournament_id))
    for round_row in round_result.scalars().all():
        if round_row.status != "finished":
            round_row.status = "cancelled"
            round_row.finished_at = now

    bracket_result = await db.execute(
        select(TournamentBracketMatch).where(TournamentBracketMatch.tournament_id == tournament_id)
    )
    match_ids: list[str] = []
    for bracket_match in bracket_result.scalars().all():
        if bracket_match.status != "finished":
            bracket_match.status = "cancelled"
            bracket_match.finished_at = now
        if bracket_match.match_id:
            match_ids.append(bracket_match.match_id)

    if match_ids:
        match_result = await db.execute(select(Match).where(Match.id.in_(match_ids)))
        for match in match_result.scalars().all():
            if match.status != "finished":
                match.status = "cancelled"
                match.finished_at = now

    await db.commit()
    await db.refresh(tournament)
    await tournament_hub.broadcast(
        tournament_id,
        {
            "type": "tournament_updated",
            "tournament_id": tournament_id,
            "reason": "admin_cancelled",
            "status": "cancelled",
        },
    )
    return tournament


async def advance_tournament_after_match(db: AsyncSession, match: Match) -> None:
    if match.status != "finished" or not match.winner_user_id:
        return

    result = await db.execute(select(TournamentBracketMatch).where(TournamentBracketMatch.match_id == match.id))
    bracket_match = result.scalar_one_or_none()
    if not bracket_match or bracket_match.status == "finished":
        return

    participants = await _load_bracket_participants(db, bracket_match)
    winner = next((participant for participant in participants if participant.user_id == match.winner_user_id), None)
    loser = next((participant for participant in participants if participant.user_id != match.winner_user_id), None)
    if not winner or not loser:
        return

    now = datetime.utcnow()
    bracket_match.status = "finished"
    bracket_match.winner_participant_id = winner.id
    bracket_match.loser_participant_id = loser.id
    bracket_match.finished_at = now

    loser.status = "eliminated"
    loser.eliminated_round = await _get_round_number(db, bracket_match.round_id)
    loser.eliminated_at = now

    await _finish_round_if_complete(db, bracket_match.round_id)

    if not bracket_match.next_bracket_match_id:
        tournament = await db.get(Tournament, bracket_match.tournament_id)
        if tournament:
            tournament.status = "finished"
            tournament.champion_user_id = winner.user_id
            tournament.finished_at = now
        winner.status = "champion"
        await _broadcast_tournament_update(
            bracket_match.tournament_id,
            "champion_decided",
            bracket_match=bracket_match,
            winner=winner,
            loser=loser,
        )
        return

    next_match = await db.get(TournamentBracketMatch, bracket_match.next_bracket_match_id)
    if not next_match:
        return
    if bracket_match.next_slot == "left":
        next_match.left_participant_id = winner.id
    else:
        next_match.right_participant_id = winner.id

    if next_match.left_participant_id and next_match.right_participant_id and not next_match.match_id:
        next_round = await db.get(TournamentRound, next_match.round_id)
        if next_round:
            next_round.status = "active"
        await _create_match_for_bracket(db, next_match)

    await _broadcast_tournament_update(
        bracket_match.tournament_id,
        "winner_advanced",
        bracket_match=bracket_match,
        winner=winner,
        loser=loser,
        next_bracket_match=next_match,
    )


def _normalize_tournament_usernames(creator_username: str, player_usernames: list[str]) -> list[str]:
    usernames = [creator_username]
    for username in player_usernames:
        normalized = username.strip()
        if normalized and normalized not in usernames:
            usernames.append(normalized)
    return usernames


async def _load_users_by_usernames(db: AsyncSession, usernames: list[str]) -> list[User]:
    result = await db.execute(select(User).where(User.username.in_(usernames)))
    by_username = {user.username: user for user in result.scalars().all()}
    missing = [username for username in usernames if username not in by_username]
    if missing:
        raise HTTPException(status_code=404, detail=f"Users not found: {', '.join(missing)}")
    return [by_username[username] for username in usernames]


async def _ensure_players_are_available(db: AsyncSession, user_ids: list[str]) -> None:
    result = await db.execute(
        select(MatchParticipant.user_id)
        .join(Match, Match.id == MatchParticipant.match_id)
        .where(Match.status == "active", MatchParticipant.user_id.in_(user_ids))
    )
    busy_ids = {user_id for user_id in result.scalars().all() if user_id}
    if busy_ids:
        users = await db.execute(select(User.username).where(User.id.in_(busy_ids)))
        names = ", ".join(users.scalars().all())
        raise HTTPException(status_code=400, detail=f"Players already have active matches: {names}")


async def _cancel_open_searches(db: AsyncSession, user_ids: list[str]) -> None:
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id.in_(user_ids),
            MatchmakingQueue.status == "searching",
        )
    )
    for queue_row in result.scalars().all():
        queue_row.status = "cancelled"


async def _seed_users_by_rating(db: AsyncSession, users: list[User]) -> list[User]:
    stats_rows = await db.execute(select(UserStats).where(UserStats.user_id.in_([user.id for user in users])))
    rating_by_user_id = {stats.user_id: stats.rating for stats in stats_rows.scalars().all()}
    return sorted(
        users,
        key=lambda user: (-(rating_by_user_id.get(user.id) or user.rating or 1200), user.username.lower()),
    )


async def _create_bracket_shell(
    db: AsyncSession,
    tournament: Tournament,
    player_count: int,
) -> tuple[list[TournamentRound], dict[int, list[TournamentBracketMatch]]]:
    total_rounds = tournament_round_count(player_count)
    rounds: list[TournamentRound] = []
    bracket_by_round: dict[int, list[TournamentBracketMatch]] = {}

    for round_number in range(1, total_rounds + 1):
        round_row = TournamentRound(
            tournament_id=tournament.id,
            round_number=round_number,
            name=tournament_round_name(round_number, total_rounds),
            status="waiting",
        )
        db.add(round_row)
        rounds.append(round_row)
    await db.flush()

    for round_row in rounds:
        match_count = player_count // (2**round_row.round_number)
        bracket_by_round[round_row.round_number] = []
        for position in range(1, match_count + 1):
            bracket_match = TournamentBracketMatch(
                tournament_id=tournament.id,
                round_id=round_row.id,
                bracket_position=position,
                status="waiting",
            )
            db.add(bracket_match)
            bracket_by_round[round_row.round_number].append(bracket_match)
    await db.flush()

    for round_number in range(1, total_rounds):
        for bracket_match in bracket_by_round[round_number]:
            next_index = (bracket_match.bracket_position - 1) // 2
            bracket_match.next_bracket_match_id = bracket_by_round[round_number + 1][next_index].id
            bracket_match.next_slot = "left" if bracket_match.bracket_position % 2 == 1 else "right"

    return rounds, bracket_by_round


async def _create_match_for_bracket(db: AsyncSession, bracket_match: TournamentBracketMatch) -> Match:
    participants = await _load_bracket_participants(db, bracket_match)
    if len(participants) != 2:
        raise HTTPException(status_code=400, detail="Tournament bracket match needs two players")

    users = [await db.get(User, participant.user_id) for participant in participants]
    if not users[0] or not users[1]:
        raise HTTPException(status_code=404, detail="Tournament player not found")

    stats = [await _get_or_create_stats(db, user) for user in users]
    match = Match(
        mode="tournament",
        status="active",
        duration_seconds=MATCH_DURATION_SECONDS,
        started_at=datetime.utcnow(),
    )
    db.add(match)
    await db.flush()

    db.add_all(
        [
            MatchParticipant(
                match_id=match.id,
                user_id=users[0].id,
                side="left",
                display_name=users[0].username,
                rating_before=stats[0].rating,
            ),
            MatchParticipant(
                match_id=match.id,
                user_id=users[1].id,
                side="right",
                display_name=users[1].username,
                rating_before=stats[1].rating,
            ),
        ]
    )

    tasks = await pick_ranked_match_tasks(db, [users[0].id, users[1].id])
    db.add_all(
        [
            MatchTask(
                match_id=match.id,
                problem_id=problem.id,
                position=index + 1,
                difficulty=problem.difficulty,
            )
            for index, problem in enumerate(tasks)
        ]
    )
    bracket_match.match_id = match.id
    bracket_match.status = "active"
    await db.flush()
    return match


async def _load_bracket_participants(
    db: AsyncSession,
    bracket_match: TournamentBracketMatch,
) -> list[TournamentParticipant]:
    participants: list[TournamentParticipant] = []
    for participant_id in [bracket_match.left_participant_id, bracket_match.right_participant_id]:
        if not participant_id:
            continue
        participant = await db.get(TournamentParticipant, participant_id)
        if participant:
            participants.append(participant)
    return participants


async def _finish_round_if_complete(db: AsyncSession, round_id: str) -> None:
    result = await db.execute(select(TournamentBracketMatch).where(TournamentBracketMatch.round_id == round_id))
    bracket_matches = list(result.scalars().all())
    if not bracket_matches or any(bracket_match.status != "finished" for bracket_match in bracket_matches):
        return
    round_row = await db.get(TournamentRound, round_id)
    if round_row:
        round_row.status = "finished"
        round_row.finished_at = datetime.utcnow()


async def _get_round_number(db: AsyncSession, round_id: str) -> int | None:
    round_row = await db.get(TournamentRound, round_id)
    return round_row.round_number if round_row else None


async def _get_or_create_stats(db: AsyncSession, user: User) -> UserStats:
    stats = await db.get(UserStats, user.id)
    if stats:
        return stats
    stats = UserStats(user_id=user.id, rating=user.rating or 1200)
    db.add(stats)
    await db.flush()
    return stats


async def _broadcast_tournament_update(
    tournament_id: str,
    reason: str,
    *,
    bracket_match: TournamentBracketMatch,
    winner: TournamentParticipant,
    loser: TournamentParticipant,
    next_bracket_match: TournamentBracketMatch | None = None,
) -> None:
    await tournament_hub.broadcast(
        tournament_id,
        {
            "type": "tournament_updated",
            "tournament_id": tournament_id,
            "reason": reason,
            "bracket_match_id": bracket_match.id,
            "match_id": bracket_match.match_id,
            "winner_participant_id": winner.id,
            "winner_user_id": winner.user_id,
            "loser_participant_id": loser.id,
            "loser_user_id": loser.user_id,
            "next_bracket_match_id": next_bracket_match.id if next_bracket_match else None,
            "status": "finished" if reason == "champion_decided" else "active",
        },
    )
