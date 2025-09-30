from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of automation actions"""
    CONNECT = "connect"
    SEND_TEXT = "send_text"
    SEND_KEY = "send_key"
    MOVE_CURSOR = "move_cursor"
    WAIT = "wait"
    WAIT_FOR_TEXT = "wait_for_text"
    READ_SCREEN = "read_screen"
    READ_POSITION = "read_position"
    ASSERT_TEXT = "assert_text"
    SCREENSHOT = "screenshot"
    DISCONNECT = "disconnect"


class AutomationStep(BaseModel):
    """Single automation step"""
    id: str = Field(..., description="Unique step identifier")
    action: ActionType = Field(..., description="Action type")
    params: dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    description: str | None = Field(None, description="Human-readable description")

    # For coordinate-based actions
    row: int | None = Field(None, ge=0, description="Terminal row (0-indexed)")
    col: int | None = Field(None, ge=0, description="Terminal column (0-indexed)")

    # For text/key actions
    text: str | None = Field(None, description="Text to send or expect")
    key: str | None = Field(None, description="Special key to send (Enter, PF1, etc)")

    # For wait actions
    timeout: float | None = Field(None, gt=0, description="Timeout in seconds")


class AutomationScript(BaseModel):
    """Complete automation script"""
    id: str = Field(..., description="Unique script identifier")
    name: str = Field(..., description="Script name")
    description: str | None = Field(None, description="Script description")
    host: str = Field(..., description="3270 host address")
    port: int = Field(default=23, description="3270 host port")
    use_tls: bool = Field(default=True, description="Use TLS connection")
    steps: list[AutomationStep] = Field(default_factory=list, description="Automation steps")
    created_at: str | None = None
    updated_at: str | None = None


class ConnectionRequest(BaseModel):
    """Request to connect to a 3270 host"""
    host: str = Field(..., description="Host address")
    port: int = Field(default=23, description="Port number")
    use_tls: bool = Field(default=True, description="Use TLS")
    session_id: str | None = Field(None, description="Optional session ID")


class TerminalInput(BaseModel):
    """Input to send to terminal"""
    session_id: str = Field(..., description="Session identifier")
    text: str | None = Field(None, description="Text to send")
    key: str | None = Field(None, description="Special key to send")
    row: int | None = Field(None, ge=0, description="Cursor row position")
    col: int | None = Field(None, ge=0, description="Cursor column position")


class ScreenData(BaseModel):
    """Terminal screen data"""
    session_id: str
    rows: int
    cols: int
    cursor_row: int
    cursor_col: int
    text: str  # Full screen text
    fields: list[dict[str, Any]] = Field(default_factory=list)  # Input fields info


class ExecutionLog(BaseModel):
    """Execution log entry"""
    step_id: str
    status: str  # success, error, running
    message: str | None = None
    timestamp: str
    screenshot: str | None = None  # Base64 encoded image
