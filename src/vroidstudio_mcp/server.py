"""FastMCP server — VRoid Studio brute-force automation with 55 archetypes."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from vroidstudio_mcp.automation import AutomationEngine
from vroidstudio_mcp.config import VRoidStudioConfig
from vroidstudio_mcp.keyboard_shortcuts import SHORTCUTS_DOCUMENTATION_URL, VRoidStudioShortcuts
from vroidstudio_mcp.recipes import OUTPUT_DIR, SCREENSHOT_DIR, focus_vroid, launch_vroid_studio, quick_gal_export
from vroidstudio_mcp.pywinauto_client import visual_screenshot, windows

logger = logging.getLogger("vroidstudio-mcp")

CONFIG = VRoidStudioConfig()
CONFIG.ensure_dirs()

_START = time.time()
_engine: AutomationEngine | None = None


def _get_engine() -> AutomationEngine:
    global _engine
    if _engine is None:
        _engine = AutomationEngine(CONFIG)
    return _engine


mcp = FastMCP(
    "vroidstudio-mcp",
    instructions=(
        "Brute-force VRoid Studio automation via pywinauto-mcp. "
        "55 config-driven archetypes with state machine, verification screenshots, and resume. "
        "Operations: status, launch, focus, screenshot, list_archetypes, run_archetype, "
        "open_project, save_project, open_and_export, run_template, "
        "quick_gal_export (legacy), list_outputs, session_status."
    ),
)


@mcp.tool()
async def vroid_studio(
    operation: Annotated[
        str,
        Field(
            description=(
                "status | launch | focus | screenshot | list_shortcuts | list_archetypes | run_archetype | "
                "run_template | open_project | save_project | save_project_as | open_and_export | "
                "list_templates | quick_gal_export | list_outputs | session_status"
            ),
        ),
    ] = "status",
    archetype_id: Annotated[str, Field(description="Archetype id for run_archetype.")] = "quick_gal",
    template_name: Annotated[str, Field(description="Template for run_template (e.g. open_and_export).")] = "",
    project_path: Annotated[str, Field(description=".vroid project path for open/save/export ops.")] = "",
    save_path: Annotated[str, Field(description=".vroid path for save_project_as.")] = "",
    output_name: Annotated[str, Field(description="Export filename.")] = "",
    pick_sample: Annotated[bool, Field(description="Legacy quick_gal_export sample pick.")] = True,
    screenshot_name: Annotated[str, Field(description="Screenshot filename.")] = "capture.png",
    session_id: Annotated[str, Field(description="Session id for resume or session_status.")] = "",
    resume: Annotated[bool, Field(description="Resume run_archetype from last good step.")] = False,
) -> dict[str, Any]:
    """VRoid Studio portmanteau — pywinauto brute-force with 55 archetypes."""
    op = operation.strip().lower()
    engine = _get_engine()

    if op == "status":
        found = await windows("find", title="VRoid Studio", base_url=CONFIG.pywinauto_url)
        running = False
        handle = None
        if found.get("success"):
            result = found.get("result")
            data = getattr(result, "data", None) if result is not None else None
            if isinstance(data, dict):
                running = bool(data.get("handle"))
                handle = data.get("handle")
        outputs = sorted(p.name for p in OUTPUT_DIR.glob("*.vrm"))
        return {
            "success": True,
            "running": running,
            "handle": handle,
            "pywinauto_url": CONFIG.pywinauto_url,
            "work_dir": str(CONFIG.work_dir),
            "outputs": outputs,
            "archetype_count": 55,
            "mode": "state_machine_pywinauto",
        }

    if op == "launch":
        return await launch_vroid_studio()

    if op == "focus":
        return await focus_vroid()

    if op == "list_shortcuts":
        shortcuts = VRoidStudioShortcuts.list_all()
        return {
            "success": True,
            "count": len(shortcuts),
            "documentation_url": SHORTCUTS_DOCUMENTATION_URL,
            "shortcuts": shortcuts,
            "note": "Use action=shortcut with shortcut=<operation> in YAML, or shortcut step name matching map key.",
        }

    if op == "list_templates":
        return {
            "success": True,
            "count": len(engine.catalog.templates),
            "templates": sorted(engine.catalog.templates.keys()),
        }

    if op == "list_archetypes":
        return engine.list_archetypes()

    if op == "run_template":
        if not template_name:
            return {"success": False, "error": "template_name required"}
        export = str((CONFIG.output_dir / output_name).resolve()) if output_name else None
        return await engine.run_template(
            template_name,
            open_path=project_path or None,
            save_path=save_path or None,
            export_path=export,
            session_id=session_id or None,
            resume=resume,
        )

    if op == "open_project":
        if not project_path:
            return {"success": False, "error": "project_path required (.vroid)"}
        return await engine.open_project(project_path)

    if op == "save_project":
        launch = await launch_vroid_studio()
        if not launch.get("success"):
            return launch
        await focus_vroid()
        from vroidstudio_mcp.pywinauto_client import keyboard as kb

        result = await kb("hotkey", keys=["ctrl", "s"], base_url=CONFIG.pywinauto_url)
        if not result.get("success"):
            return result
        return {"success": True, "operation": "save_project"}

    if op == "save_project_as":
        if not save_path:
            return {"success": False, "error": "save_path required (.vroid)"}
        return await engine.save_project_as(save_path)

    if op == "open_and_export":
        if not project_path:
            return {"success": False, "error": "project_path required (.vroid)"}
        fname = output_name or "exported.vrm"
        return await engine.open_and_export(project_path, fname)

    if op == "run_archetype":
        name = output_name or None
        return await engine.run_archetype(
            archetype_id,
            session_id=session_id or None,
            resume=resume,
            output_name=name,
        )

    if op == "session_status":
        if not session_id:
            return {"success": False, "error": "session_id required"}
        path = CONFIG.session_dir / f"{session_id}.json"
        if not path.is_file():
            return {"success": False, "error": f"Session not found: {session_id}"}
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return {"success": True, "session": data}

    if op == "screenshot":
        path = SCREENSHOT_DIR / screenshot_name
        found = await windows("find", title="VRoid Studio", base_url=CONFIG.pywinauto_url)
        handle = None
        if found.get("success"):
            result = found.get("result")
            data = getattr(result, "data", None) if result is not None else None
            if isinstance(data, dict):
                handle = data.get("handle")
        shot = await visual_screenshot(
            output_path=str(path),
            window_handle=handle,
            base_url=CONFIG.pywinauto_url,
        )
        if not shot.get("success"):
            return shot
        return {"success": True, "path": str(path), "operation": op}

    if op == "quick_gal_export":
        fname = output_name or "anime_gal.vrm"
        return await quick_gal_export(fname, pick_sample=pick_sample)

    if op == "list_outputs":
        files = []
        for p in OUTPUT_DIR.glob("*"):
            if p.is_file():
                files.append({"name": p.name, "size_kb": round(p.stat().st_size / 1024, 1)})
        return {"success": True, "files": files, "output_dir": str(OUTPUT_DIR)}

    return {"success": False, "error": f"Unknown operation: {operation}"}


class ToolCallBody(BaseModel):
    tool: str
    arguments: dict[str, Any] | None = None


app = FastAPI(title="vroidstudio-mcp", version="0.3.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "uptime_s": round(time.time() - _START, 1), "archetypes": 55}


@app.get("/api/v1/download/{filename}")
async def download_file(filename: str):
    path = OUTPUT_DIR / filename
    if not path.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(path)


@app.post("/api/v1/control/tool")
async def control_tool(body: ToolCallBody):
    try:
        if body.tool == "vroid_studio":
            return await vroid_studio(**(body.arguments or {}))
        return {"success": False, "error": f"Unknown tool: {body.tool}"}
    except Exception as exc:
        logger.exception("tool call failed")
        return {"success": False, "error": str(exc)}


app.mount("/mcp", mcp.http_app())


def main() -> None:
    import asyncio
    import sys

    logging.basicConfig(level=logging.INFO)
    if "--stdio" in sys.argv or os.environ.get("MCP_STDIO_MODE", "").lower() in ("1", "true", "yes"):
        asyncio.run(mcp.run_stdio_async(show_banner=False))
        return
    host = os.environ.get("VROIDSTUDIO_MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("VROIDSTUDIO_MCP_PORT", "10881"))
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
