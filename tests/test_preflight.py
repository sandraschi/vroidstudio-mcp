"""Tests for system-admin preflight (mocked)."""

from pathlib import Path

import pytest

from vroidstudio_mcp.preflight import PreflightConfig, run_preflight


@pytest.mark.asyncio
async def test_preflight_disabled(tmp_path: Path):
    result = await run_preflight(
        output_dir=tmp_path,
        config=PreflightConfig(enabled=False),
    )
    assert result.ok
    assert result.checks[0]["skipped"] is True


@pytest.mark.asyncio
async def test_preflight_disk_fail(tmp_path: Path, monkeypatch):
    class FakeUsage:
        free = 100 * 1024 * 1024

    monkeypatch.setattr("vroidstudio_mcp.preflight.shutil.disk_usage", lambda _p: FakeUsage())

    result = await run_preflight(
        output_dir=tmp_path,
        config=PreflightConfig(enabled=True, min_disk_mb=500),
    )
    assert not result.ok
    assert "disk" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_preflight_memory_fail(tmp_path: Path, monkeypatch):
    async def fake_perf(**_kwargs):
        return {
            "success": True,
            "data": {
                "memory": {"available_bytes": 500 * 1024 * 1024, "percent": 90},
                "cpu": {"total_percent": 10},
            },
        }

    monkeypatch.setattr("vroidstudio_mcp.preflight.get_performance_metrics", fake_perf)

    result = await run_preflight(
        output_dir=tmp_path,
        config=PreflightConfig(enabled=True, min_memory_mb=2048, min_disk_mb=100),
    )
    assert not result.ok
    assert "memory" in (result.error or "").lower()
