"""Runtime configuration for vroidstudio-mcp."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_vroid_studio_path() -> str:
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "VRoidStudio"
    if local.is_dir():
        versions = sorted(local.glob("*/VRoidStudio.exe"), reverse=True)
        if versions:
            return str(versions[0])
    return r"C:\Program Files\VRoidStudio\VRoidStudio.exe"


def _repo_config_dir() -> Path:
    env = os.environ.get("VROIDSTUDIO_MCP_CONFIG_DIR")
    if env:
        return Path(env)
    bundled = Path(__file__).resolve().parent / "config"
    if bundled.is_dir():
        return bundled
    return Path(__file__).resolve().parents[2] / "config"


@dataclass
class VRoidStudioConfig:
    vroid_studio_path: str = field(
        default_factory=lambda: os.environ.get("VROIDSTUDIO_PATH")
        or _default_vroid_studio_path()
    )
    pywinauto_url: str = field(
        default_factory=lambda: (
            os.environ.get("CUA_MCP_URL")
            or os.environ.get("PYWINAUTO_MCP_URL")
            or "http://127.0.0.1:10789"
        )
    )
    work_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("VROIDSTUDIO_MCP_WORK_DIR", Path(os.environ.get("TEMP", ".")) / "vroidstudio_mcp")
        )
    )
    config_dir: Path = field(default_factory=_repo_config_dir)
    auto_launch: bool = True
    timeout_s: float = 60.0
    max_retries: int = 3
    retry_delay_s: float = 1.0
    stable_poll_interval_s: float = 0.4
    stable_frames_required: int = 3
    stable_timeout_s: float = 15.0
    verify_ui_change: bool = True
    use_cua_assert: bool = field(
        default_factory=lambda: os.environ.get("VROID_USE_CUA_ASSERT", "1").strip().lower() not in ("0", "false", "no")
    )
    use_cua_dialog: bool = field(
        default_factory=lambda: os.environ.get("VROID_USE_CUA_DIALOG", "1").strip().lower() not in ("0", "false", "no")
    )
    use_cua_shortcut: bool = field(
        default_factory=lambda: os.environ.get("VROID_USE_CUA_SHORTCUT", "1").strip().lower() not in ("0", "false", "no")
    )
    use_cua_task: bool = field(
        default_factory=lambda: os.environ.get("VROID_USE_CUA_TASK", "1").strip().lower() not in ("0", "false", "no")
    )
    use_sysadmin_preflight: bool = field(
        default_factory=lambda: os.environ.get("VROID_USE_SYSADMIN_PREFLIGHT", "1").strip().lower()
        not in ("0", "false", "no")
    )
    system_admin_url: str = field(
        default_factory=lambda: os.environ.get("SYSTEM_ADMIN_MCP_URL", "http://127.0.0.1:10861")
    )
    preflight_min_memory_mb: float = field(
        default_factory=lambda: float(os.environ.get("VROID_PREFLIGHT_MIN_MEMORY_MB", "2048"))
    )
    preflight_min_disk_mb: float = field(
        default_factory=lambda: float(os.environ.get("VROID_PREFLIGHT_MIN_DISK_MB", "500"))
    )
    hash_algorithm: str = field(
        default_factory=lambda: os.environ.get("VROID_HASH_ALGORITHM", "dhash")
    )
    change_threshold_pct: float = field(
        default_factory=lambda: float(os.environ.get("VROID_CHANGE_THRESHOLD_PCT", "1.0"))
    )
    baseline_width: int = 1920
    baseline_height: int = 1080

    def stable_region(self) -> dict[str, int] | None:
        """Optional crop for stability/verify (editor canvas only).

        Env vars override cua-mcp vroidstudio profile defaults (T2.4).
        """
        keys = ("VROID_STABLE_REGION_LEFT", "VROID_STABLE_REGION_TOP", "VROID_STABLE_REGION_RIGHT", "VROID_STABLE_REGION_BOTTOM")
        if all(os.environ.get(k) for k in keys):
            return {
                "region_left": int(os.environ["VROID_STABLE_REGION_LEFT"]),
                "region_top": int(os.environ["VROID_STABLE_REGION_TOP"]),
                "region_right": int(os.environ["VROID_STABLE_REGION_RIGHT"]),
                "region_bottom": int(os.environ["VROID_STABLE_REGION_BOTTOM"]),
            }
        use_profile = os.environ.get("VROID_USE_PROFILE_REGION", "1").strip().lower() not in ("0", "false", "no")
        if use_profile:
            return {
                "region_left": 280,
                "region_top": 120,
                "region_right": 1640,
                "region_bottom": 980,
            }
        return None

    @property
    def screenshot_dir(self) -> Path:
        return self.work_dir / "screenshots"

    @property
    def output_dir(self) -> Path:
        return self.work_dir / "output"

    @property
    def failure_dir(self) -> Path:
        return self.work_dir / "failures"

    @property
    def session_dir(self) -> Path:
        return self.work_dir / "sessions"

    @property
    def archetypes_path(self) -> Path:
        return self.config_dir / "archetypes.yaml"

    @property
    def defaults_path(self) -> Path:
        return self.config_dir / "defaults.yaml"

    @property
    def projects_dir(self) -> Path:
        return self.work_dir / "projects"

    def ensure_dirs(self) -> None:
        for d in (
            self.screenshot_dir,
            self.output_dir,
            self.failure_dir,
            self.session_dir,
            self.projects_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def scale_x(self, x: int) -> int:
        scale = float(os.environ.get("VROID_UI_SCALE_X", "1.0"))
        return int(x * scale)

    def scale_y(self, y: int) -> int:
        scale = float(os.environ.get("VROID_UI_SCALE_Y", "1.0"))
        return int(y * scale)
