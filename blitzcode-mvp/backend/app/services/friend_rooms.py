from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FriendRoom, Match, MatchEvent, MatchParticipant, MatchTask, MatchmakingQueue, User, UserStats
from app.services.matchmaker import MATCH_DURATION_SECONDS, get_active_match_for_user
from app.services.task_picker import pick_ranked_match_tasks


ROOM_TTL_MINUTES = 30


async def create_friend_room(db: AsyncSession, creator: User, opponent_username: str) -> FriendRoom:
    invited = await _get_user_by_username(db, opponent_username)
    if invited.id == creator.id:
        raise HTTPException(status_code=400, detail="Invite another user, not yourself")

    active_match = await get_active_match_for_user(db, creator.id)
    if active_match:
        raise HTTPException(status_code=400, detail="Finish your active match before creating a room")

    await _cancel_open_searches(db, creator.id)
    await _expire_old_rooms(db)

    existing = await db.execute(
        select(FriendRoom)
        .where(
            FriendRoom.creator_user_id == creator.id,
            FriendRoom.invited_user_id == invited.id,
            FriendRoom.status == "pending",
        )
        .order_by(desc(FriendRoom.created_at))
        .limit(1)
    )
    room = existing.scalar_one_or_none()
    if room:
        await db.commit()
        await db.refresh(room)
        return room

    creator_stats = await _get_or_create_stats(db, creator)
    match = Match(
        mode="friend",
        status="waiting",
        duration_seconds=MATCH_DURATION_SECONDS,
    )
    db.add(match)
    await db.flush()
    db.add(
        MatchParticipant(
            match_id=match.id,
            user_id=creator.id,
            side="right",
            display_name=creator.username,
            rating_before=creator_stats.rating,
        )
    )
    room = FriendRoom(
        match_id=match.id,
        creator_user_id=creator.id,
        invited_user_id=invited.id,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(minutes=ROOM_TTL_MINUTES),
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def accept_friend_room(db: AsyncSession, room_id: str, user: User) -> FriendRoom:
    await _expire_old_rooms(db)
    room = await db.get(FriendRoom, room_id)
    if not room or room.invited_user_id != user.id:
        raise HTTPException(status_code=404, detail="Room invite not found")
    if room.status != "pending":
        raise HTTPException(status_code=400, detail="Room is no longer pending")

    active_match = await get_active_match_for_user(db, user.id)
    if active_match:
        raise HTTPException(status_code=400, detail="Finish your active match before joining a room")

    creator = await db.get(User, room.creator_user_id)
    match = await db.get(Match, room.match_id)
    if not creator or not match:
        raise HTTPException(status_code=404, detail="Room match not found")

    invited_stats = await _get_or_create_stats(db, user)
    db.add(
        MatchParticipant(
            match_id=match.id,
            user_id=user.id,
            side="left",
            display_name=user.username,
            rating_before=invited_stats.rating,
        )
    )
    tasks = await pick_ranked_match_tasks(db, [creator.id, user.id])
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
    now = datetime.utcnow()
    match.status = "active"
    match.started_at = now
    room.status = "accepted"
    room.accepted_at = now
    db.add(
        MatchEvent(
            match_id=match.id,
            user_id=user.id,
            type="friend_room_accepted",
            payload={"room_id": room.id, "creator_user_id": creator.id, "invited_user_id": user.id},
        )
    )
    await db.commit()
    await db.refresh(room)
    return room


async def cancel_friend_room(db: AsyncSession, room_id: str, user: User) -> FriendRoom:
    await _expire_old_rooms(db)
    room = await db.get(FriendRoom, room_id)
    if not room or user.id not in {room.creator_user_id, room.invited_user_id}:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending rooms can be cancelled")

    match = await db.get(Match, room.match_id)
    room.status = "cancelled"
    if match and match.status == "waiting":
        match.status = "cancelled"
    db.add(
        MatchEvent(
            match_id=room.match_id,
            user_id=user.id,
            type="friend_room_cancelled",
            payload={"room_id": room.id},
        )
    )
    await db.commit()
    await db.refresh(room)
    return room


async def get_friend_room(db: AsyncSession, room_id: str, user: User) -> FriendRoom:
    await _expire_old_rooms(db)
    room = await db.get(FriendRoom, room_id)
    if not room or user.id not in {room.creator_user_id, room.invited_user_id}:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


async def list_pending_invites(db: AsyncSession, user: User) -> list[FriendRoom]:
    await _expire_old_rooms(db)
    result = await db.execute(
        select(FriendRoom)
        .where(FriendRoom.invited_user_id == user.id, FriendRoom.status == "pending")
        .order_by(desc(FriendRoom.created_at))
        .limit(20)
    )
    return list(result.scalars().all())


async def list_my_rooms(db: AsyncSession, user: User) -> list[FriendRoom]:
    await _expire_old_rooms(db)
    result = await db.execute(
        select(FriendRoom)
        .where(or_(FriendRoom.creator_user_id == user.id, FriendRoom.invited_user_id == user.id))
        .order_by(desc(FriendRoom.created_at))
        .limit(20)
    )
    return list(result.scalars().all())


async def _get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).where(User.username == username.strip()))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User with this login was not found")
    return user


async def _get_or_create_stats(db: AsyncSession, user: User) -> UserStats:
    stats = await db.get(UserStats, user.id)
    if stats:
        return stats
    stats = UserStats(user_id=user.id, rating=user.rating or 1200)
    db.add(stats)
    await db.flush()
    return stats


async def _cancel_open_searches(db: AsyncSession, user_id: str) -> None:
    result = await db.execute(
        select(MatchmakingQueue).where(
            MatchmakingQueue.user_id == user_id,
            MatchmakingQueue.status == "searching",
        )
    )
    for row in result.scalars().all():
        row.status = "cancelled"


async def _expire_old_rooms(db: AsyncSession) -> None:
    now = datetime.utcnow()
    result = await db.execute(
        select(FriendRoom).where(
            FriendRoom.status == "pending",
            FriendRoom.expires_at.is_not(None),
            FriendRoom.expires_at < now,
        )
    )
    changed = False
    for room in result.scalars().all():
        room.status = "expired"
        match = await db.get(Match, room.match_id)
        if match and match.status == "waiting":
            match.status = "expired"
        changed = True
    if changed:
        await db.commit()
