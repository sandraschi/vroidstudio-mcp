"""Preflight checks via system-admin-mcp before VRoid automation."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vroidstudio_mcp.sysadmin_client import (
    get_performance_metrics,
    list_processes,
)

logger = logging.getLogger(__name__)


@dataclass
class PreflightConfig:
    enabled: bool = True
    min_memory_mb: float = 2048.0
    min_disk_mb: float = 500.0
    max_cpu_percent: float = 95.0
    require_vroid_process: bool = False
    vroid_process_names: tuple[str, ...] = ("VRoidStudio", "VRoid Studio")
    sysadmin_url: str = ""


@dataclass
class PreflightResult:
    ok: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": self.checks,
            "warnings": self.warnings,
            "error": self.error,
        }


async def run_preflight(
    *,
    output_dir: Path,
    config: PreflightConfig,
) -> PreflightResult:
    """Verify host resources and optional VRoid process before automation."""
    if not config.enabled:
        return PreflightResult(ok=True, checks=[{"name": "preflight", "skipped": True}])

    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    base_url = config.sysadmin_url or None

    disk = shutil.disk_usage(output_dir)
    free_mb = disk.free / (1024 * 1024)
    disk_ok = free_mb >= config.min_disk_mb
    checks.append(
        {
            "name": "disk_free",
            "path": str(output_dir),
            "free_mb": round(free_mb, 1),
            "min_mb": config.min_disk_mb,
            "passed": disk_ok,
        }
    )
    if not disk_ok:
        return PreflightResult(
            ok=False,
            checks=checks,
            error=f"Insufficient disk space on {output_dir}: {free_mb:.0f}MB < {config.min_disk_mb}MB",
        )

    perf = await get_performance_metrics(base_url=base_url)
    if not perf.get("success"):
        warnings.append(f"system-admin metrics unavailable: {perf.get('error')}")
        checks.append({"name": "memory", "skipped": True, "reason": perf.get("error")})
        checks.append({"name": "cpu", "skipped": True, "reason": perf.get("error")})
    else:
        data = perf.get("data") or perf.get("result") or {}
        mem = data.get("memory") or {}
        avail_bytes = float(mem.get("available_bytes") or 0)
        avail_mb = avail_bytes / (1024 * 1024)
        mem_ok = avail_mb >= config.min_memory_mb
        checks.append(
            {
                "name": "memory_available",
                "available_mb": round(avail_mb, 1),
                "min_mb": config.min_memory_mb,
                "percent_used": mem.get("percent"),
                "passed": mem_ok,
            }
        )
        if not mem_ok:
            return PreflightResult(
                ok=False,
                checks=checks,
                warnings=warnings,
                error=f"Low memory: {avail_mb:.0f}MB available < {config.min_memory_mb}MB",
            )

        cpu = data.get("cpu") or {}
        cpu_total = float(cpu.get("total_percent") or 0)
        cpu_ok = cpu_total <= config.max_cpu_percent
        checks.append(
            {
                "name": "cpu_load",
                "total_percent": cpu_total,
                "max_percent": config.max_cpu_percent,
                "passed": cpu_ok,
            }
        )
        if not cpu_ok:
            warnings.append(f"High CPU load ({cpu_total:.0f}%) — automation may be slow")

    if config.require_vroid_process:
        found = False
        for proc_name in config.vroid_process_names:
            proc = await list_processes(filter_name=proc_name, base_url=base_url)
            if proc.get("success"):
                result = proc.get("data") or proc.get("result") or {}
                total = int(result.get("total") or 0)
                if total > 0:
                    found = True
                    checks.append(
                        {
                            "name": "vroid_process",
                            "filter": proc_name,
                            "count": total,
                            "passed": True,
                        }
                    )
                    break
        if not found:
            checks.append({"name": "vroid_process", "passed": False})
            return PreflightResult(
                ok=False,
                checks=checks,
                warnings=warnings,
                error="VRoid Studio process not found (require_vroid_process=true)",
            )

    return PreflightResult(ok=True, checks=checks, warnings=warnings)
