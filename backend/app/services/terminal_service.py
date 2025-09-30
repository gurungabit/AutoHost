import uuid
import asyncio
import re
from typing import Optional
from tnz.py3270 import Emulator
from app.schemas.automation import ScreenData


class TerminalSession:
    """Represents a single 3270 terminal session"""

    def __init__(self, session_id: str, host: str, port: int, use_tls: bool = True):
        self.session_id = session_id
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.connection: Optional[Emulator] = None
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
        self.connection = Emulator(visible=False)
        # Build connection string with TLS if needed
        protocol = "L:" if self.use_tls else ""
        host_string = f"{protocol}{self.host}:{self.port}"
        self.connection.Connect(host_string)

    async def disconnect(self):
        """Disconnect from the host"""
        if self.connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.connection.Disconnect)
            self.is_connected = False

    async def send_text(self, text: str, row: Optional[int] = None, col: Optional[int] = None):
        """Send text to the terminal"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _send():
            if row is not None and col is not None:
                # Move cursor then send text (rows/cols are 0-indexed in API, 1-indexed in emulator)
                self.connection.MoveCursor(row + 1, col + 1)
            self.connection.String(text)

        await loop.run_in_executor(None, _send)

    async def send_key(self, key: str):
        """Send a special key (Enter, PF1, etc)"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _send():
            key_lower = key.lower()
            # Handle Enter
            if key_lower == "enter":
                self.connection.Enter()
            # Handle PF keys
            elif key_lower.startswith("pf"):
                num = int(key_lower[2:])
                self.connection.PF(num)
            # Handle PA keys
            elif key_lower.startswith("pa"):
                num = int(key_lower[2:])
                self.connection.PA(num)
            # Handle Clear
            elif key_lower == "clear":
                self.connection.Clear()
            # Handle Tab
            elif key_lower == "tab":
                self.connection.Tab()
            # Handle BackTab
            elif key_lower == "backtab":
                self.connection.BackTab()
            else:
                # Fallback to Key method
                self.connection.Key(key)

        await loop.run_in_executor(None, _send)

    async def move_cursor(self, row: int, col: int):
        """Move cursor to position"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()
        # Convert 0-indexed to 1-indexed
        await loop.run_in_executor(None, self.connection.MoveCursor, row + 1, col + 1)

    async def get_screen_data(self) -> ScreenData:
        """Get current screen data"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _get_data():
            # Query screen status to get dimensions and cursor position
            # Format: 'L U U N N ? 24 80 0 0 0x00 -'
            # Positions: ... rows cols cursor_row cursor_col ...
            status = self.connection.Query('Cursor')
            status_line = status[1] if len(status) > 1 else ""
            parts = status_line.split()

            # Default values
            rows = 24
            cols = 80
            cursor_row = 0
            cursor_col = 0

            if len(parts) >= 10:
                try:
                    rows = int(parts[6])
                    cols = int(parts[7])
                    cursor_row = int(parts[8])
                    cursor_col = int(parts[9])
                except (ValueError, IndexError):
                    pass

            # Get full screen text using Ascii
            screen_lines = self.connection.Ascii()
            text = '\n'.join(screen_lines) if isinstance(screen_lines, list) else str(screen_lines)

            # Debug logging
            import sys
            print(f"[DEBUG] Screen query status: {status}", file=sys.stderr)
            print(f"[DEBUG] Parsed - rows: {rows}, cols: {cols}, cursor: ({cursor_row}, {cursor_col})", file=sys.stderr)
            print(f"[DEBUG] Screen lines type: {type(screen_lines)}, count: {len(screen_lines) if isinstance(screen_lines, list) else 'N/A'}", file=sys.stderr)
            print(f"[DEBUG] Text length: {len(text)}, preview: {text[:100] if text else 'EMPTY'}", file=sys.stderr)

            # Get field information
            fields = []

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
            # Use Ascii to get screen content and extract the text
            screen_lines = self.connection.Ascii()
            if isinstance(screen_lines, list) and 0 <= row < len(screen_lines):
                line = screen_lines[row]
                return line[col:col+length] if col < len(line) else ""
            return ""

        return await loop.run_in_executor(None, _read)

    async def wait_for_text(self, text: str, timeout: float = 10.0) -> bool:
        """Wait for specific text to appear on screen"""
        if not self.connection:
            raise Exception("Not connected")

        loop = asyncio.get_event_loop()

        def _wait():
            try:
                # Use Emulator's Expect method if available
                self.connection.Expect(text, timeout=int(timeout))
                return True
            except:
                # If Expect fails or times out, return False
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
