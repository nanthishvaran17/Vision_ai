from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.security.jwt import decode_access_token
from app.logging import logger

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
        logger.info("websocket_client_connected", conversation_id=conversation_id)

    def disconnect(self, conversation_id: str, websocket: WebSocket):
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
        logger.info("websocket_client_disconnected", conversation_id=conversation_id)

    async def broadcast_to_conversation(self, conversation_id: str, event_type: str, data: dict):
        if conversation_id in self.active_connections:
            payload = {"event": event_type, "data": data}
            dead_sockets = []
            for ws in self.active_connections[conversation_id]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ds in dead_sockets:
                self.disconnect(conversation_id, ds)

manager = ConnectionManager()

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/conversations/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...)
):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(conversation_id, websocket)
    try:
        while True:
            # Keepalive / Listen for ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
