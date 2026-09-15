from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import WebSocket


class TournamentHub:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, tournament_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[tournament_id].add(websocket)

    def disconnect(self, tournament_id: str, websocket: WebSocket) -> None:
        sockets = self._connections.get(tournament_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(tournament_id, None)

    async def broadcast(self, tournament_id: str, event: dict[str, Any]) -> None:
        sockets = list(self._connections.get(tournament_id, set()))
        for websocket in sockets:
            try:
                await websocket.send_json(_json_safe(event))
            except Exception:
                self.disconnect(tournament_id, websocket)


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


tournament_hub = TournamentHub()
