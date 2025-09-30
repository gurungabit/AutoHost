from fastapi import APIRouter, HTTPException
from app.schemas.automation import ConnectionRequest, TerminalInput, ScreenData
from app.services.terminal_service import terminal_manager

router = APIRouter()


@router.post("/connect")
async def connect_terminal(request: ConnectionRequest):
    """Connect to a 3270 host"""
    try:
        # Create session
        session_id = terminal_manager.create_session(
            host=request.host,
            port=request.port,
            use_tls=request.use_tls
        )

        # Get session and connect
        session = terminal_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=500, detail="Failed to create session")

        await session.connect()

        return {
            "session_id": session_id,
            "host": request.host,
            "port": request.port,
            "status": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disconnect/{session_id}")
async def disconnect_terminal(session_id: str):
    """Disconnect from a 3270 host"""
    try:
        await terminal_manager.remove_session(session_id)
        return {"status": "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {"sessions": terminal_manager.list_sessions()}


@router.get("/screen/{session_id}")
async def get_screen(session_id: str) -> ScreenData:
    """Get current screen data"""
    session = terminal_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        return await session.get_screen_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/input")
async def send_input(input_data: TerminalInput):
    """Send input to terminal"""
    session = terminal_manager.get_session(input_data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Move cursor if position specified
        if input_data.row is not None and input_data.col is not None:
            await session.move_cursor(input_data.row, input_data.col)

        # Send text if provided
        if input_data.text:
            await session.send_text(input_data.text)

        # Send key if provided
        if input_data.key:
            await session.send_key(input_data.key)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
