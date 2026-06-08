#!/usr/bin/env python3
"""Fleet smoke test: cua-mcp + system-admin + vroidstudio export path.

Run with backends up (see scripts/smoke_start.ps1). Without VRoid Studio installed,
validates API wiring, profiles, templates, preflight, and archetype catalog only.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

CUA_URL = os.environ.get("CUA_MCP_URL", "http://127.0.0.1:10789").rstrip("/")
SYSADMIN_URL = os.environ.get("SYSTEM_ADMIN_MCP_URL", "http://127.0.0.1:10861").rstrip("/")
VROID_URL = os.environ.get("VROIDSTUDIO_MCP_URL", "http://127.0.0.1:10881").rstrip("/")
ARCHETYPE = os.environ.get("SMOKE_ARCHETYPE", "quick_gal")
RUN_EXPORT = os.environ.get("SMOKE_RUN_EXPORT", "0").strip().lower() in ("1", "true", "yes")


def _ok(label: str) -> None:
    print(f"  OK  {label}")


def _fail(label: str, detail: str) -> None:
    print(f"  FAIL {label}: {detail}")
    raise SystemExit(1)


def _unwrap(raw: Any) -> Any:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        sc = raw.get("structured_content")
        if isinstance(sc, dict) and isinstance(sc.get("data"), dict):
            return sc["data"]
        if "data" in raw and isinstance(raw["data"], dict):
            return raw["data"]
        if "content" in raw and isinstance(raw["content"], list):
            return _unwrap(raw["content"])
        if "result" in raw:
            return _unwrap(raw["result"])
        if raw.get("status") == "success" and isinstance(raw.get("data"), dict):
            return raw["data"]
        return raw
    if isinstance(raw, list):
        for block in raw:
            if isinstance(block, dict) and block.get("text"):
                try:
                    parsed = json.loads(block["text"])
                    return _unwrap(parsed)
                except json.JSONDecodeError:
                    continue
    return raw


def _get(client: httpx.Client, url: str, label: str) -> dict[str, Any]:
    try:
        r = client.get(url, timeout=15.0)
        r.raise_for_status()
        _ok(label)
        body = r.json() if r.content else {}
        return body if isinstance(body, dict) else {}
    except Exception as exc:
        _fail(label, str(exc))
        return {}


def _cua_tool(client: httpx.Client, name: str, arguments: dict[str, Any], label: str) -> dict[str, Any]:
    try:
        r = client.post(
            f"{CUA_URL}/api/v1/tools/call",
            json={"name": name, "arguments": arguments},
            timeout=120.0,
        )
        r.raise_for_status()
        body = r.json()
        if body.get("status") == "error":
            _fail(label, body.get("message", "tool error"))
        _ok(label)
        return _unwrap(body.get("result"))
    except Exception as exc:
        _fail(label, str(exc))
        return {}


def _sysadmin_tool(client: httpx.Client, name: str, arguments: dict[str, Any], label: str) -> dict[str, Any]:
    try:
        r = client.post(
            f"{SYSADMIN_URL}/api/tools/call",
            json={"name": name, "arguments": arguments},
            timeout=60.0,
        )
        r.raise_for_status()
        body = r.json()
        if body.get("status") == "error":
            _fail(label, body.get("message", "tool error"))
        _ok(label)
        return _unwrap(body.get("result"))
    except Exception as exc:
        _fail(label, str(exc))
        return {}


def _vroid_tool(client: httpx.Client, arguments: dict[str, Any], label: str) -> dict[str, Any]:
    try:
        r = client.post(
            f"{VROID_URL}/api/v1/control/tool",
            json={"tool": "vroid_studio", "arguments": arguments},
            timeout=600.0,
        )
        r.raise_for_status()
        body = r.json()
        if not body.get("success", True) and body.get("error"):
            _fail(label, body.get("error", "tool error"))
        _ok(label)
        return body if isinstance(body, dict) else {}
    except Exception as exc:
        _fail(label, str(exc))
        return {}


def main() -> int:
    print("=== VRoid fleet smoke test ===")
    vroid_exe = Path(os.environ.get("VROIDSTUDIO_PATH", r"C:\Program Files\VRoidStudio\VRoidStudio.exe"))
    has_vroid = vroid_exe.is_file()
    print(f"VRoid Studio: {'found' if has_vroid else 'NOT INSTALLED'} ({vroid_exe})")

    with httpx.Client() as client:
        _get(client, f"{CUA_URL}/api/v1/health", "cua-mcp health")
        _get(client, f"{SYSADMIN_URL}/api/health", "system-admin-mcp health")
        _get(client, f"{VROID_URL}/health", "vroidstudio-mcp health")

        profiles_payload = _cua_tool(
            client,
            "automation_task",
            {"request": {"operation": "list_profiles"}},
            "cua-mcp list_profiles",
        )
        profiles = profiles_payload.get("profiles", [])
        vroid_profile = next((p for p in profiles if p.get("app_id") == "vroidstudio"), None)
        if not vroid_profile or "stable_region" not in vroid_profile:
            _fail("vroidstudio profile region", "stable_region missing from list_profiles")

        templates_payload = _cua_tool(
            client,
            "automation_task",
            {"request": {"operation": "list_templates", "app": "vroidstudio"}},
            "cua-mcp list_templates",
        )
        tmpl_list = templates_payload.get("templates", [])
        if len(tmpl_list) < 1:
            _fail("template library", "no templates listed")

        status = _get(client, f"{SYSADMIN_URL}/api/status", "system-admin status (preflight)")
        mem = (status.get("system") or {}).get("memory") or {}
        if not mem.get("available"):
            _fail("preflight metrics", "memory block missing from /api/status")

        # Note: /api/tools/call can hang on this host; REST /api/status is the reliable preflight path.

        archetypes = _vroid_tool(client, {"operation": "list_archetypes"}, "vroidstudio list_archetypes")
        count = archetypes.get("count", 0)
        if count < 55:
            _fail("archetype catalog", f"expected 55+, got {count}")

        if RUN_EXPORT and has_vroid:
            print(f"--- Live export smoke: {ARCHETYPE} ---")
            out_name = f"smoke_{ARCHETYPE}.vrm"
            result = _vroid_tool(
                client,
                {
                    "operation": "run_archetype",
                    "archetype_id": ARCHETYPE,
                    "output_name": out_name,
                },
                f"run_archetype {ARCHETYPE}",
            )
            if not result.get("success"):
                _fail("run_archetype", json.dumps(result, indent=2)[:500])
            export_path = result.get("export_path", "")
            if export_path and not Path(export_path).is_file():
                _fail("export file", f"missing {export_path}")
            _ok(f"export {export_path}")
        elif RUN_EXPORT:
            print("SKIP live export (VRoid Studio not installed).")
        else:
            print("SKIP live export (SMOKE_RUN_EXPORT not set). API/template/profile checks passed.")

    print("=== smoke PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
