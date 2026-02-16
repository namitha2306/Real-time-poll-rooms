from fastapi import WebSocket
from typing import Dict, List
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, poll_id: str, websocket: WebSocket):
        await websocket.accept()

        if poll_id not in self.active_connections:
            self.active_connections[poll_id] = []

        self.active_connections[poll_id].append(websocket)

        # Broadcast updated viewer count
        await self.broadcast(poll_id, {
            "type": "viewer_update",
            "viewers": len(self.active_connections[poll_id])
        })

    def disconnect(self, poll_id: str, websocket: WebSocket):
        if poll_id in self.active_connections:
            if websocket in self.active_connections[poll_id]:
                self.active_connections[poll_id].remove(websocket)

            if len(self.active_connections[poll_id]) == 0:
                del self.active_connections[poll_id]
            else:
                asyncio.create_task(
                    self.broadcast(poll_id, {
                        "type": "viewer_update",
                        "viewers": len(self.active_connections[poll_id])
                    })
                )

    async def broadcast(self, poll_id: str, message: dict):
        if poll_id in self.active_connections:
            for connection in self.active_connections[poll_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()
