"""VRoid Studio brute-force recipes — legacy wrappers over AutomationEngine."""

from __future__ import annotations

from typing import Any

from vroidstudio_mcp.automation import AutomationEngine
from vroidstudio_mcp.config import VRoidStudioConfig

_config = VRoidStudioConfig()
OUTPUT_DIR = _config.output_dir
SCREENSHOT_DIR = _config.screenshot_dir


async def launch_vroid_studio() -> dict[str, Any]:
    engine = AutomationEngine(_config)
    return await engine.launch_vroid()


async def focus_vroid(handle: int | None = None) -> dict[str, Any]:
    engine = AutomationEngine(_config)
    if handle:
        engine._handle = handle
    return await engine.focus_vroid()


async def quick_gal_export(
    output_name: str = "anime_gal.vrm",
    *,
    pick_sample: bool = True,
    export_wait_s: float = 8.0,
) -> dict[str, Any]:
    """Fleet legacy recipe — maps to quick_gal archetype."""
    engine = AutomationEngine(_config)
    archetype_id = "quick_gal" if pick_sample else "blank_female"
    if output_name != "anime_gal.vrm":
        return await engine.run_archetype(archetype_id, output_name=output_name)
    return await engine.run_archetype(archetype_id, output_name=output_name or "quick_gal.vrm")
