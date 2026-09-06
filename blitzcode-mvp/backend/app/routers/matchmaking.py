from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Match, MatchmakingQueue, User
from app.schemas import FriendRoomCreateIn, FriendRoomOut, MatchmakingJoinResponse, MatchmakingStatusResponse
from app.services.matchmaker import (
    cancel_ranked_queue,
    get_active_match_for_user,
    join_ranked_queue,
    refresh_ranked_queue,
)
from app.services.bot_match import create_bot_match
from app.services.friend_rooms import (
    accept_friend_room,
    cancel_friend_room,
    create_friend_room,
    get_friend_room,
    list_my_rooms,
    list_pending_invites,
)
from app.services.past_self_match import create_past_self_match
from app.services.rate_limiter import matchmaking_rate_limiter


router = APIRouter(prefix="/api/matchmaking", tags=["matchmaking"])


@router.post("/join", response_model=MatchmakingJoinResponse)
async def join_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "join")
    match = await join_ranked_queue(db, current_user)
    if match:
        return MatchmakingJoinResponse(
            status="matched",
            match_id=match.id,
            message="Match found.",
        )
    return MatchmakingJoinResponse(
        status="searching",
        message="Searching for an opponent near your rating.",
    )


@router.post("/bot", response_model=MatchmakingJoinResponse)
async def start_bot_match(
    level: str = "auto",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "bot")
    match = await create_bot_match(db, current_user, level=level)
    return MatchmakingJoinResponse(
        status="matched",
        match_id=match.id,
        message="Bot match ready.",
    )


@router.post("/past-self", response_model=MatchmakingJoinResponse)
async def start_past_self_match(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "past-self")
    match = await create_past_self_match(db, current_user)
    if not match:
        raise HTTPException(status_code=404, detail="Finish one match before racing your past self")
    return MatchmakingJoinResponse(
        status="matched",
        match_id=match.id,
        message="Past-self match ready.",
    )


@router.post("/rooms", response_model=FriendRoomOut)
async def create_room(
    payload: FriendRoomCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-create")
    room = await create_friend_room(db, current_user, payload.opponent_username)
    return await _room_out(db, room)


@router.get("/rooms", response_model=list[FriendRoomOut])
async def my_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-list")
    rooms = await list_my_rooms(db, current_user)
    return [await _room_out(db, room) for room in rooms]


@router.get("/rooms/invites", response_model=list[FriendRoomOut])
async def pending_room_invites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-invites")
    rooms = await list_pending_invites(db, current_user)
    return [await _room_out(db, room) for room in rooms]


@router.get("/rooms/{room_id}", response_model=FriendRoomOut)
async def room_status(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-status")
    room = await get_friend_room(db, room_id, current_user)
    return await _room_out(db, room)


@router.post("/rooms/{room_id}/accept", response_model=FriendRoomOut)
async def accept_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-accept")
    room = await accept_friend_room(db, room_id, current_user)
    return await _room_out(db, room)


@router.post("/rooms/{room_id}/cancel", response_model=FriendRoomOut)
async def cancel_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "room-cancel")
    room = await cancel_friend_room(db, room_id, current_user)
    return await _room_out(db, room)


@router.post("/cancel")
async def cancel_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "cancel")
    changed = await cancel_ranked_queue(db, current_user.id)
    return {"cancelled": changed}


@router.get("/status", response_model=MatchmakingStatusResponse)
async def queue_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_matchmaking_rate_limit(current_user, "status")
    refreshed = await refresh_ranked_queue(db, current_user)
    if isinstance(refreshed, Match):
        return MatchmakingStatusResponse(status="matched", match_id=refreshed.id)
    if isinstance(refreshed, MatchmakingQueue):
        return MatchmakingStatusResponse(
            status=refreshed.status,
            match_id=refreshed.matched_match_id,
            rating_min=refreshed.rating_min,
            rating_max=refreshed.rating_max,
        )

    result = await db.execute(
        select(MatchmakingQueue)
        .where(
            MatchmakingQueue.user_id == current_user.id,
            MatchmakingQueue.status.in_(["searching", "matched"]),
        )
        .order_by(MatchmakingQueue.queued_at.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        active_match = await get_active_match_for_user(db, current_user.id)
        if active_match:
            return MatchmakingStatusResponse(status="matched", match_id=active_match.id)
        return MatchmakingStatusResponse(status="idle")
    return MatchmakingStatusResponse(
        status=row.status,
        match_id=row.matched_match_id,
        rating_min=row.rating_min,
        rating_max=row.rating_max,
    )


def _check_matchmaking_rate_limit(user: User, action: str) -> None:
    result = matchmaking_rate_limiter.check(
        f"matchmaking:{action}:user:{user.id}",
        limit=settings.matchmaking_rate_limit_count,
        window_seconds=settings.matchmaking_rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many matchmaking requests. Try again in {result.retry_after_seconds} seconds.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )


async def _room_out(db: AsyncSession, room) -> FriendRoomOut:
    creator = await db.get(User, room.creator_user_id)
    invited = await db.get(User, room.invited_user_id)
    return FriendRoomOut(
        id=room.id,
        match_id=room.match_id,
        status=room.status,
        creator_user_id=room.creator_user_id,
        creator_username=creator.username if creator else "unknown",
        invited_user_id=room.invited_user_id,
        invited_username=invited.username if invited else "unknown",
        created_at=room.created_at,
        accepted_at=room.accepted_at,
        expires_at=room.expires_at,
    )
