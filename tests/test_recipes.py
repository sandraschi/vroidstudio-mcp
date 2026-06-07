"""Offline tests for recipes and work dirs."""

from vroidstudio_mcp.recipes import OUTPUT_DIR, SCREENSHOT_DIR


def test_work_dirs_defined():
    assert "output" in str(OUTPUT_DIR).lower()
    assert "screenshot" in str(SCREENSHOT_DIR).lower()
