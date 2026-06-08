#!/usr/bin/env python3
"""In-process live export smoke (bypasses hung HTTP tool bridge)."""
import asyncio
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "VROIDSTUDIO_PATH",
    r"C:\Users\sandr\AppData\Local\Programs\VRoidStudio\2.3.0\VRoidStudio.exe",
)
os.environ.setdefault("VROID_USE_CUA_TASK", "1")
os.environ.setdefault("VROID_USE_SYSADMIN_PREFLIGHT", "0")

from vroidstudio_mcp.automation import AutomationEngine
from vroidstudio_mcp.config import VRoidStudioConfig


async def main() -> int:
    archetype = os.environ.get("SMOKE_ARCHETYPE", "quick_gal")
    cfg = VRoidStudioConfig()
    cfg.vroid_studio_path = os.environ["VROIDSTUDIO_PATH"]
    cfg.use_sysadmin_preflight = False
    engine = AutomationEngine(cfg)

    print(f"Launch/focus VRoid ({cfg.vroid_studio_path}) ...")
    launch = await engine.launch_vroid()
    print("launch:", launch)
    if not launch.get("success"):
        return 1
    focus = await engine.focus_vroid()
    print("focus:", focus)
    if not focus.get("success"):
        return 1

    print(f"run_archetype: {archetype}")
    result = await engine.run_archetype(archetype, output_name=f"smoke_{archetype}.vrm")
    print(result)
    if not result.get("success"):
        return 1
    export_path = result.get("export_path", "")
    if export_path and Path(export_path).is_file():
        print(f"OK export: {export_path} ({Path(export_path).stat().st_size} bytes)")
        return 0
    print("FAIL: export file missing")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
