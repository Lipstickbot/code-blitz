from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, get_user_from_token
from app.config import settings
from app.database import get_db
from app.models import Tournament, User
from app.schemas import (
    TournamentCreateIn,
    TournamentOut,
)
from app.services.rate_limiter import matchmaking_rate_limiter
from app.services.tournament_hub import tournament_hub
from app.services.tournaments import create_tournament, get_tournament_for_user, list_my_tournaments
from app.services.tournament_views import tournament_out


router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.post("", response_model=TournamentOut)
async def create_tournament_room(
    payload: TournamentCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "create")
    tournament = await create_tournament(db, current_user, payload.name, payload.player_usernames)
    return await tournament_out(db, tournament)


@router.get("", response_model=list[TournamentOut])
async def my_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "list")
    tournaments = await list_my_tournaments(db, current_user)
    return [await tournament_out(db, tournament) for tournament in tournaments]


@router.get("/{tournament_id}", response_model=TournamentOut)
async def tournament_detail(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "detail")
    tournament = await get_tournament_for_user(db, tournament_id, current_user)
    return await tournament_out(db, tournament)


@router.get("/{tournament_id}/bracket", response_model=TournamentOut)
async def tournament_bracket(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "bracket")
    tournament = await get_tournament_for_user(db, tournament_id, current_user)
    return await tournament_out(db, tournament)


@router.get("/{tournament_id}/spectate", response_model=TournamentOut)
async def tournament_spectate(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_tournament_rate_limit(current_user, "spectate")
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return await tournament_out(db, tournament)


@router.websocket("/{tournament_id}/stream")
async def stream_tournament(tournament_id: str, websocket: WebSocket, token: str | None = None):
    async for db in get_db():
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=4401)
            return

        tournament = await db.get(Tournament, tournament_id)
        if not tournament:
            await websocket.close(code=4404)
            return

        await tournament_hub.connect(tournament_id, websocket)
        await websocket.send_json(
            {
                "type": "snapshot",
                "tournament_id": tournament.id,
                "status": tournament.status,
                "player_count": tournament.player_count,
                "champion_user_id": tournament.champion_user_id,
            }
        )

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            tournament_hub.disconnect(tournament_id, websocket)
        return


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
