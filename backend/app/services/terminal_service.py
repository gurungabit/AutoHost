import uuid
import asyncio
from typing import Optional
from tnz import ati
from app.schemas.automation import ScreenData


class TerminalSession:
    """Represents a single 3270 terminal session"""

    def __init__(self, session_id: str, host: str, port: int, use_tls: bool = True):
        self.session_id = session_id
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.connection: Optional[ati.Ati] = None
        self.is_connected = False

    async def connect(self):
        """Connect to the 3270 host"""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._sync_connect
            )
            self.is_connected = True
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to {self.host}:{self.port} - {str(e)}")

    def _sync_connect(self):
        """Synchronous connection (runs in executor)"""
        self.connection = ati.Ati()
        # Connect with or without TLS
        if self.use_tls:
            self.connection.connect(f"{self.host}:{self.port}", tls=True)
        else:
            self.connection.connect(f"{self.host}:{self.port}")

    async def disconnect(self):
        """Disconnect from the host"""
        if self.connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.connection.disconnect)
            self.is_connected = False

    async def send_text(self, text: str, row: Optional[int] = None, col: Optional[int] = None):
        """Send text to the terminal"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _send():
            if row is not None and col is not None:
                # Move cursor then send text
                self.connection.move_to(row, col)
            self.connection.send_text(text)

        await loop.run_in_executor(None, _send)

    async def send_key(self, key: str):
        """Send a special key (Enter, PF1, etc)"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _send():
            # Map common key names to tnz key codes
            key_map = {
                "enter": "Enter",
                "pf1": "PF1", "pf2": "PF2", "pf3": "PF3",
                "pf4": "PF4", "pf5": "PF5", "pf6": "PF6",
                "pf7": "PF7", "pf8": "PF8", "pf9": "PF9",
                "pf10": "PF10", "pf11": "PF11", "pf12": "PF12",
                "pa1": "PA1", "pa2": "PA2", "pa3": "PA3",
                "clear": "Clear",
                "tab": "Tab",
                "backtab": "BackTab",
            }
            tnz_key = key_map.get(key.lower(), key)
            self.connection.send_key(tnz_key)

        await loop.run_in_executor(None, _send)

    async def move_cursor(self, row: int, col: int):
        """Move cursor to position"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.connection.move_to, row, col)

    async def get_screen_data(self) -> ScreenData:
        """Get current screen data"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _get_data():
            # Get screen dimensions
            rows = self.connection.screen_rows
            cols = self.connection.screen_cols

            # Get cursor position
            cursor_row, cursor_col = self.connection.cursor_position

            # Get full screen text
            text = self.connection.screen_text

            # Get field information
            fields = []
            # tnz provides field information - we can extend this

            return ScreenData(
                session_id=self.session_id,
                rows=rows,
                cols=cols,
                cursor_row=cursor_row,
                cursor_col=cursor_col,
                text=text,
                fields=fields
            )

        return await loop.run_in_executor(None, _get_data)

    async def read_text(self, row: int, col: int, length: int) -> str:
        """Read text at specific position"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _read():
            return self.connection.read_text(row, col, length)

        return await loop.run_in_executor(None, _read)

    async def wait_for_text(self, text: str, timeout: float = 10.0) -> bool:
        """Wait for specific text to appear on screen"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _wait():
            # Simple polling implementation
            import time
            start = time.time()
            while time.time() - start < timeout:
                screen = self.connection.screen_text
                if text in screen:
                    return True
                time.sleep(0.1)
            return False

        return await loop.run_in_executor(None, _wait)


class TerminalManager:
    """Manages multiple terminal sessions"""

    def __init__(self):
        self.sessions: dict[str, TerminalSession] = {}

    def create_session(self, host: str, port: int, use_tls: bool = True) -> str:
        """Create a new terminal session"""
        session_id = str(uuid.uuid4())
        session = TerminalSession(session_id, host, port, use_tls)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)

    async def remove_session(self, session_id: str):
        """Remove and disconnect a session"""
        session = self.sessions.get(session_id)
        if session:
            if session.is_connected:
                await session.disconnect()
            del self.sessions[session_id]

    def list_sessions(self) -> list[dict]:
        """List all active sessions"""
        return [
            {
                "session_id": sid,
                "host": session.host,
                "port": session.port,
                "is_connected": session.is_connected
            }
            for sid, session in self.sessions.items()
        ]


# Global terminal manager instance
terminal_manager = TerminalManager()
