import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.terminal_service import terminal_manager

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@router.websocket("/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time terminal streaming"""
    await manager.connect(websocket, session_id)

    try:
        # Start screen update loop
        update_task = asyncio.create_task(
            send_screen_updates(websocket, session_id)
        )

        # Listen for commands from client
        while True:
            data = await websocket.receive_json()
            command = data.get("command")

            if command == "input":
                await handle_input_command(session_id, data)
            elif command == "disconnect":
                break

    except WebSocketDisconnect:
        pass
    finally:
        update_task.cancel()
        manager.disconnect(session_id)


async def send_screen_updates(websocket: WebSocket, session_id: str):
    """Send periodic screen updates to client"""
    session = terminal_manager.get_session(session_id)
    if not session:
        return

    try:
        while True:
            if session.is_connected:
                try:
                    screen_data = await session.get_screen_data()
                    await websocket.send_json({
                        "type": "screen_update",
                        "data": screen_data.model_dump()
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })

            await asyncio.sleep(1.0)  # Update every 1 second
    except asyncio.CancelledError:
        pass


async def handle_input_command(session_id: str, data: dict):
    """Handle input command from client"""
    session = terminal_manager.get_session(session_id)
    if not session:
        return

    try:
        text = data.get("text")
        key = data.get("key")
        row = data.get("row")
        col = data.get("col")

        if row is not None and col is not None:
            await session.move_cursor(row, col)

        if text:
            await session.send_text(text)

        if key:
            await session.send_key(key)

    except Exception as e:
        # Error will be sent in next screen update
        pass
