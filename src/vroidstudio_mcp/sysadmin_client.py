"""HTTP client for system-admin-mcp — process and resource preflight."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _default_sysadmin_url() -> str:
    return os.environ.get("SYSTEM_ADMIN_MCP_URL", "http://127.0.0.1:10861")


DEFAULT_SYSADMIN_URL = _default_sysadmin_url()


async def call_system_admin_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Call system-admin-mcp POST /api/tools/call."""
    url = (base_url or DEFAULT_SYSADMIN_URL).rstrip("/") + "/api/tools/call"
    payload = {"name": tool_name, "arguments": arguments}
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.warning("system-admin-mcp call failed tool=%s error=%s", tool_name, exc)
        return {"success": False, "error": str(exc), "tool": tool_name}

    if body.get("status") == "error":
        return {"success": False, "error": body.get("message", "tool error"), "tool": tool_name}

    result = body.get("result")
    if isinstance(result, dict) and result.get("status") == "error":
        return {
            "success": False,
            "error": result.get("error", result.get("message", "tool error")),
            "data": result,
            "tool": tool_name,
        }

    return {"success": True, "result": result, "data": result, "tool": tool_name}


async def system_admin_operation(
    operation: str,
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
    **fields: Any,
) -> dict[str, Any]:
    """Invoke the system_admin portmanteau tool."""
    args: dict[str, Any] = {"operation": operation, **fields}
    return await call_system_admin_tool("system_admin", args, base_url=base_url, timeout=timeout)


async def list_processes(
    *,
    filter_name: str | None = None,
    sort_by: str = "cpu",
    page_size: int = 20,
    base_url: str | None = None,
) -> dict[str, Any]:
    return await system_admin_operation(
        "list_processes",
        filter_name=filter_name,
        sort_by=sort_by,
        page_size=page_size,
        base_url=base_url,
    )


async def get_performance_metrics(*, base_url: str | None = None) -> dict[str, Any]:
    return await system_admin_operation("get_performance_metrics", base_url=base_url)


async def get_top_resource_processes(
    *,
    limit: int = 10,
    base_url: str | None = None,
) -> dict[str, Any]:
    return await system_admin_operation("get_top_resource_processes", limit=limit, base_url=base_url)
