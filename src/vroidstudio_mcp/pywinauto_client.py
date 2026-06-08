"""HTTP client for cua-mcp (pywinauto-mcp) REST tool bridge."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_PYWINAUTO_URL = os.environ.get("PYWINAUTO_MCP_URL", "http://127.0.0.1:10789")


def parse_tool_result(raw: Any) -> dict[str, Any]:
    """Normalize FastMCP / API tool payload to ToolResult-shaped dict."""
    if raw is None:
        return {"status": "error", "message": "empty tool result"}

    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "success", "message": raw, "data": {"text": raw}}

    if isinstance(raw, list):
        for block in raw:
            if isinstance(block, dict):
                text = block.get("text")
                if text:
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict) and "status" in parsed:
                            return parsed
                    except json.JSONDecodeError:
                        continue
                if block.get("type") == "text" and block.get("text"):
                    try:
                        return json.loads(block["text"])
                    except json.JSONDecodeError:
                        pass
        return {"status": "error", "message": "unparseable tool result list"}

    if isinstance(raw, dict):
        if "status" in raw and "message" in raw:
            return raw
        if "result" in raw:
            return parse_tool_result(raw["result"])
        if "data" in raw and isinstance(raw["data"], dict) and "status" in raw["data"]:
            return raw["data"]

    return {"status": "error", "message": f"unexpected tool result type: {type(raw).__name__}"}


async def call_pywinauto_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    base_url: str | None = None,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Call cua-mcp POST /api/v1/tools/call."""
    url = (base_url or DEFAULT_PYWINAUTO_URL).rstrip("/") + "/api/v1/tools/call"
    payload = {"name": tool_name, "arguments": arguments}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.warning("cua-mcp call failed tool=%s error=%s", tool_name, exc)
        return {"success": False, "error": str(exc), "tool": tool_name}

    if body.get("status") == "error":
        return {"success": False, "error": body.get("message", "tool error"), "tool": tool_name}

    tool_result = parse_tool_result(body.get("result"))
    if tool_result.get("status") == "error":
        return {
            "success": False,
            "error": tool_result.get("message", "tool error"),
            "data": tool_result.get("data"),
            "recovery_tip": tool_result.get("recovery_tip"),
            "tool": tool_name,
        }

    return {
        "success": True,
        "result": tool_result,
        "data": tool_result.get("data"),
        "tool": tool_name,
    }


async def automation_dialog(
    operation: str,
    *,
    base_url: str | None = None,
    timeout: float = 120.0,
    **fields: Any,
) -> dict[str, Any]:
    """Call automation_dialog on cua-mcp."""
    req: dict[str, Any] = {"operation": operation, **fields}
    return await call_pywinauto_tool(
        "automation_dialog",
        {"request": req},
        base_url=base_url,
        timeout=timeout,
    )


async def automation_assert(
    operation: str,
    *,
    base_url: str | None = None,
    timeout: float = 120.0,
    **fields: Any,
) -> dict[str, Any]:
    """Call automation_assert on cua-mcp."""
    req: dict[str, Any] = {"operation": operation, **fields}
    return await call_pywinauto_tool(
        "automation_assert",
        {"request": req},
        base_url=base_url,
        timeout=timeout,
    )


async def keyboard(
    operation: str,
    *,
    text: str = "",
    key: str = "",
    keys: list[str] | None = None,
    pause: float = 0.05,
    base_url: str | None = None,
) -> dict[str, Any]:
    req: dict[str, Any] = {"operation": operation, "pause": pause}
    if text:
        req["text"] = text
    if key:
        req["key"] = key
    if keys:
        req["keys"] = keys
    return await call_pywinauto_tool("automation_keyboard", {"request": req}, base_url=base_url)


async def windows(
    operation: str,
    *,
    title: str = "VRoid Studio",
    handle: int | None = None,
    action: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    req: dict[str, Any] = {"operation": operation, "title": title, "partial": True}
    if handle is not None:
        req["handle"] = handle
    if action:
        req["action"] = action
    return await call_pywinauto_tool("automation_windows", {"request": req}, base_url=base_url)


async def visual_screenshot(
    *,
    output_path: str,
    window_handle: int | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    req: dict[str, Any] = {
        "operation": "screenshot",
        "output_path": output_path,
        "format": "png",
    }
    if window_handle is not None:
        req["window_handle"] = window_handle
    return await call_pywinauto_tool("automation_visual", {"request": req}, base_url=base_url)


async def mouse_click(x: int, y: int, *, base_url: str | None = None) -> dict[str, Any]:
    req = {"operation": "click", "x": x, "y": y}
    return await call_pywinauto_tool("automation_mouse", {"request": req}, base_url=base_url)
