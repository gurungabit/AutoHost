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
        import sys
        import time
        # Try with specific terminal model (common 3270 models)
        self.connection = Emulator(visible=False)

        # Set common 3270 terminal characteristics
        try:
            # Many systems expect IBM-3278-2 or similar
            print(f"[DEBUG] Setting up emulator options", file=sys.stderr)
        except Exception as e:
            print(f"[DEBUG] Emulator setup failed: {e}", file=sys.stderr)
        # Build connection string with TLS if needed
        protocol = "L:" if self.use_tls else ""
        host_string = f"{protocol}{self.host}:{self.port}"
        print(f"[DEBUG] Connecting to: {host_string}", file=sys.stderr)
        self.connection.Connect(host_string)

        # Wait for connection to be fully established
        print(f"[DEBUG] Waiting for connection to stabilize...", file=sys.stderr)
        time.sleep(2)  # Give time for initial screen

        # Try different methods to get initial screen
        try:
            # Method 1: Wait for any output
            print(f"[DEBUG] Trying Wait('Output')", file=sys.stderr)
            self.connection.Wait('Output', timeout=5)
        except Exception as e:
            print(f"[DEBUG] Wait Output failed: {e}", file=sys.stderr)
            try:
                # Method 2: Send Enter to wake up the system
                print(f"[DEBUG] Sending Enter to wake up system", file=sys.stderr)
                self.connection.Enter()
                time.sleep(1)
            except Exception as e2:
                print(f"[DEBUG] Enter failed: {e2}", file=sys.stderr)

        # Try to trigger initial screen
        try:
            # Some systems need a key press to show login screen
            print(f"[DEBUG] Sending PF1 to trigger screen", file=sys.stderr)
            self.connection.PF(1)
            time.sleep(1)
        except Exception as e:
            print(f"[DEBUG] PF1 failed: {e}", file=sys.stderr)

        # Check emulator status
        try:
            status = self.connection.Query()
            print(f"[DEBUG] Emulator status after setup: {status}", file=sys.stderr)

            # Try to get current screen
            screen_lines = self.connection.Ascii()
            if isinstance(screen_lines, list) and len(screen_lines) > 0:
                print(f"[DEBUG] Initial screen has {len(screen_lines)} lines", file=sys.stderr)
                print(f"[DEBUG] First line after setup: {screen_lines[0]!r}", file=sys.stderr)

        except Exception as e:
            print(f"[DEBUG] Status check failed: {e}", file=sys.stderr)

        print(f"[DEBUG] Connection setup complete", file=sys.stderr)

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
            # Ascii() returns list like: ['data: line1', 'data: line2', ...]
            # We need to strip the 'data: ' prefix
            screen_lines = self.connection.Ascii()

            import sys
            print(f"[DEBUG] Ascii() returned type: {type(screen_lines)}", file=sys.stderr)
            if isinstance(screen_lines, list):
                print(f"[DEBUG] Number of lines: {len(screen_lines)}", file=sys.stderr)
                if len(screen_lines) > 0:
                    print(f"[DEBUG] First line: {screen_lines[0]!r}", file=sys.stderr)
                    if len(screen_lines) > 12:
                        print(f"[DEBUG] Middle line (12): {screen_lines[12]!r}", file=sys.stderr)
                    print(f"[DEBUG] Last line: {screen_lines[-1]!r}", file=sys.stderr)

            if isinstance(screen_lines, list):
                # Strip 'data: ' prefix if present and filter status lines
                cleaned_lines = []
                for line in screen_lines:
                    if isinstance(line, str):
                        if line.startswith('data: '):
                            cleaned_lines.append(line[6:])  # Remove 'data: ' prefix
                        elif not line.startswith(('ok', 'error')):
                            cleaned_lines.append(line)
                text = '\n'.join(cleaned_lines)
                print(f"[DEBUG] Cleaned text length: {len(text)}, lines: {len(cleaned_lines)}", file=sys.stderr)
            else:
                text = str(screen_lines)
                print(f"[DEBUG] Screen text (as string): {text[:100]}", file=sys.stderr)

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
