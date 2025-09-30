import json
import os
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.automation import AutomationScript, AutomationStep, ExecutionLog
from app.services.terminal_service import terminal_manager
from app.core.config import settings

router = APIRouter()


def get_scripts_dir() -> Path:
    """Get scripts directory path"""
    scripts_dir = Path(settings.scripts_dir)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir


def get_logs_dir() -> Path:
    """Get logs directory path"""
    logs_dir = Path(settings.logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


@router.get("/scripts")
async def list_scripts():
    """List all automation scripts"""
    scripts_dir = get_scripts_dir()
    scripts = []

    for file_path in scripts_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                script_data = json.load(f)
                scripts.append({
                    "id": script_data.get("id"),
                    "name": script_data.get("name"),
                    "description": script_data.get("description"),
                    "host": script_data.get("host"),
                    "steps_count": len(script_data.get("steps", []))
                })
        except Exception:
            continue

    return {"scripts": scripts}


@router.get("/scripts/{script_id}")
async def get_script(script_id: str) -> AutomationScript:
    """Get a specific automation script"""
    scripts_dir = get_scripts_dir()
    file_path = scripts_dir / f"{script_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")

    try:
        with open(file_path, "r") as f:
            script_data = json.load(f)
            return AutomationScript(**script_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load script: {str(e)}")


@router.post("/scripts")
async def create_script(script: AutomationScript):
    """Create a new automation script"""
    scripts_dir = get_scripts_dir()
    file_path = scripts_dir / f"{script.id}.json"

    if file_path.exists():
        raise HTTPException(status_code=400, detail="Script already exists")

    try:
        # Add timestamps
        script.created_at = datetime.utcnow().isoformat()
        script.updated_at = script.created_at

        with open(file_path, "w") as f:
            json.dump(script.model_dump(), f, indent=2)

        return {"status": "created", "script_id": script.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create script: {str(e)}")


@router.put("/scripts/{script_id}")
async def update_script(script_id: str, script: AutomationScript):
    """Update an existing automation script"""
    scripts_dir = get_scripts_dir()
    file_path = scripts_dir / f"{script_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")

    try:
        # Update timestamp
        script.updated_at = datetime.utcnow().isoformat()

        with open(file_path, "w") as f:
            json.dump(script.model_dump(), f, indent=2)

        return {"status": "updated", "script_id": script_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update script: {str(e)}")


@router.delete("/scripts/{script_id}")
async def delete_script(script_id: str):
    """Delete an automation script"""
    scripts_dir = get_scripts_dir()
    file_path = scripts_dir / f"{script_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")

    try:
        file_path.unlink()
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete script: {str(e)}")


@router.post("/execute/{script_id}")
async def execute_script(script_id: str):
    """Execute an automation script"""
    # Load script
    script = await get_script(script_id)

    # Create session
    session_id = terminal_manager.create_session(
        host=script.host,
        port=script.port,
        use_tls=script.use_tls
    )

    session = terminal_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session")

    logs: list[ExecutionLog] = []

    try:
        # Connect
        await session.connect()
        logs.append(ExecutionLog(
            step_id="connect",
            status="success",
            message=f"Connected to {script.host}:{script.port}",
            timestamp=datetime.utcnow().isoformat()
        ))

        # Execute steps
        for step in script.steps:
            try:
                await execute_step(session, step)
                logs.append(ExecutionLog(
                    step_id=step.id,
                    status="success",
                    message=f"Executed: {step.action}",
                    timestamp=datetime.utcnow().isoformat()
                ))
            except Exception as e:
                logs.append(ExecutionLog(
                    step_id=step.id,
                    status="error",
                    message=str(e),
                    timestamp=datetime.utcnow().isoformat()
                ))
                break

        return {"status": "completed", "session_id": session_id, "logs": logs}

    except Exception as e:
        await terminal_manager.remove_session(session_id)
        raise HTTPException(status_code=500, detail=str(e))


async def execute_step(session, step: AutomationStep):
    """Execute a single automation step"""
    from app.schemas.automation import ActionType

    if step.action == ActionType.SEND_TEXT:
        if step.row is not None and step.col is not None:
            await session.send_text(step.text or "", step.row, step.col)
        else:
            await session.send_text(step.text or "")

    elif step.action == ActionType.SEND_KEY:
        await session.send_key(step.key or "enter")

    elif step.action == ActionType.MOVE_CURSOR:
        if step.row is not None and step.col is not None:
            await session.move_cursor(step.row, step.col)

    elif step.action == ActionType.WAIT:
        import asyncio
        await asyncio.sleep(step.timeout or 1.0)

    elif step.action == ActionType.WAIT_FOR_TEXT:
        success = await session.wait_for_text(step.text or "", step.timeout or 10.0)
        if not success:
            raise Exception(f"Timeout waiting for text: {step.text}")

    elif step.action == ActionType.READ_SCREEN:
        screen_data = await session.get_screen_data()
        # Could save or return screen data

    elif step.action == ActionType.ASSERT_TEXT:
        screen_data = await session.get_screen_data()
        if step.text and step.text not in screen_data.text:
            raise Exception(f"Assertion failed: '{step.text}' not found on screen")

    elif step.action == ActionType.DISCONNECT:
        await session.disconnect()
