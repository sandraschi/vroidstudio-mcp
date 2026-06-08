"""Atomic automation operations with verification and failure logging."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vroidstudio_mcp.archetypes import ArchetypeCatalog, StepDef, load_catalog
from vroidstudio_mcp.config import VRoidStudioConfig
from vroidstudio_mcp.keyboard_shortcuts import SHORTCUTS_DOCUMENTATION_URL, VRoidStudioShortcuts
from vroidstudio_mcp.pywinauto_client import automation_assert, keyboard, mouse_click, visual_screenshot, windows
from vroidstudio_mcp.state_machine import SessionState, WorkflowState

logger = logging.getLogger(__name__)

_MUTATION_ACTIONS = frozenset(
    {
        "shortcut",
        "hotkey",
        "press",
        "type",
        "click",
        "sample_click",
        "export_vrm",
        "export_dialog",
        "open_file",
        "save_file",
    }
)


def _file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AutomationEngine:
    def __init__(self, config: VRoidStudioConfig | None = None) -> None:
        self.config = config or VRoidStudioConfig()
        self.config.ensure_dirs()
        self.catalog = load_catalog(self.config.archetypes_path, self.config.defaults_path)
        self._handle: int | None = None
        self._session: SessionState | None = None

    def _scale_click(self, x: int | None, y: int | None) -> tuple[int | None, int | None]:
        if x is None or y is None:
            return x, y
        return self.config.scale_x(x), self.config.scale_y(y)

    async def _screenshot(self, name: str) -> Path:
        path = self.config.screenshot_dir / name
        result = await visual_screenshot(
            output_path=str(path),
            window_handle=self._handle,
            base_url=self.config.pywinauto_url,
        )
        if not result.get("success"):
            raise RuntimeError(result.get("error", "screenshot failed"))
        return path

    def _assert_request_base(self) -> dict[str, Any]:
        req: dict[str, Any] = {}
        region = self.config.stable_region()
        if region:
            req.update(region)
        return req

    async def _wait_stable(self, label: str) -> Path:
        if self.config.use_cua_assert and self._handle:
            fields: dict[str, Any] = {
                "window_handle": self._handle,
                "stable_frames_required": self.config.stable_frames_required,
                "poll_interval_s": self.config.stable_poll_interval_s,
                "timeout_s": self.config.stable_timeout_s,
                "hash_algorithm": self.config.hash_algorithm,
                "output_dir": str(self.config.screenshot_dir),
                **self._assert_request_base(),
            }
            result = await automation_assert("wait_stable", base_url=self.config.pywinauto_url, **fields)
            if result.get("success"):
                data = result.get("data") or {}
                shot = data.get("screenshot_path")
                if shot and Path(shot).is_file():
                    return Path(shot)
            logger.warning(
                "cua-mcp wait_stable failed for %s (%s) — falling back to local hash poll",
                label,
                result.get("error"),
            )

        return await self._wait_stable_local(label)

    async def _wait_stable_local(self, label: str) -> Path:
        deadline = time.monotonic() + self.config.stable_timeout_s
        last_hash = ""
        stable_count = 0
        last_path = self.config.screenshot_dir / f"stable_{label}.png"
        while time.monotonic() < deadline:
            path = await self._screenshot(f"stable_{label}_{stable_count}.png")
            current = _file_hash(path)
            if current and current == last_hash:
                stable_count += 1
                if stable_count >= self.config.stable_frames_required:
                    path.replace(last_path)
                    return last_path
            else:
                stable_count = 1
                last_hash = current
                last_path = path
            await asyncio.sleep(self.config.stable_poll_interval_s)
        raise TimeoutError(f"UI did not stabilize within {self.config.stable_timeout_s}s ({label})")

    def _failure_path(self, step_name: str) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        arch = self._session.archetype_id if self._session else "unknown"
        return self.config.failure_dir / f"{ts}_{arch}_{step_name}.png"

    async def _verify_change(self, before: Path, after: Path, step: StepDef) -> None:
        if not step.require_change or not self.config.verify_ui_change:
            return

        step_name = step.name or step.action
        diff_path = str(self.config.screenshot_dir / f"diff_{step_name}.png")

        if self.config.use_cua_assert:
            fields: dict[str, Any] = {
                "image_path": str(before),
                "image_path_b": str(after),
                "change_threshold_pct": self.config.change_threshold_pct,
                "output_path": diff_path,
                **self._assert_request_base(),
            }
            result = await automation_assert("assert_changed", base_url=self.config.pywinauto_url, **fields)
            if result.get("success"):
                return
            data = result.get("data") or {}
            if "changed_pct" in data:
                tip = result.get("recovery_tip") or ""
                raise RuntimeError(
                    f"UI unchanged after step '{step_name}' "
                    f"({data['changed_pct']}% < {self.config.change_threshold_pct}%). {tip}"
                )
            logger.warning(
                "cua-mcp assert_changed unavailable (%s) — falling back to local hash",
                result.get("error"),
            )

        if _file_hash(before) == _file_hash(after):
            raise RuntimeError(f"UI unchanged after step '{step_name}' — expected visual change")

    def _set_state(self, state: WorkflowState) -> None:
        if self._session:
            self._session.state = state

    def _save_session(self) -> None:
        if not self._session:
            return
        path = self.config.session_dir / f"{self._session.session_id}.json"
        path.write_text(json.dumps(self._session.to_dict(), indent=2), encoding="utf-8")

    async def launch_vroid(self) -> dict[str, Any]:
        self._set_state(WorkflowState.LAUNCHING)
        found = await windows("find", title="VRoid Studio", base_url=self.config.pywinauto_url)
        if found.get("success"):
            data = _extract_handle(found)
            if data:
                self._handle = data
                self._set_state(WorkflowState.LAUNCHED)
                return {"success": True, "launched": False, "handle": data}

        exe = Path(self.config.vroid_studio_path)
        if not exe.is_file():
            return {"success": False, "error": f"VRoid Studio not found: {exe}"}

        subprocess.Popen(
            [str(exe)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        for _ in range(int(self.config.timeout_s / 2)):
            await asyncio.sleep(2.0)
            found = await windows("find", title="VRoid Studio", base_url=self.config.pywinauto_url)
            data = _extract_handle(found) if found.get("success") else None
            if data:
                self._handle = data
                self._set_state(WorkflowState.LAUNCHED)
                return {"success": True, "launched": True, "handle": data}

        self._set_state(WorkflowState.FAILED)
        return {"success": False, "error": "VRoid Studio did not appear within timeout"}

    async def focus_vroid(self) -> dict[str, Any]:
        if not self._handle:
            found = await windows("find", title="VRoid Studio", base_url=self.config.pywinauto_url)
            self._handle = _extract_handle(found) if found.get("success") else None
        if not self._handle:
            return {"success": False, "error": "VRoid window not found"}
        result = await windows("focus", handle=self._handle, base_url=self.config.pywinauto_url)
        if result.get("success"):
            self._set_state(WorkflowState.FOCUSED)
        return result

    async def _execute_step(self, step: StepDef, export_path_holder: dict[str, str]) -> None:
        step_name = step.name or step.action
        before = await self._screenshot(f"before_{step_name}.png")

        for attempt in range(self.config.max_retries):
            try:
                if step.action in _MUTATION_ACTIONS and self._handle:
                    focus = await self.focus_vroid()
                    if not focus.get("success"):
                        raise RuntimeError(focus.get("error", "focus failed before step"))
                await self._run_step_action(step, export_path_holder)
                await self._wait_stable(step_name)
                after = await self._screenshot(f"after_{step_name}.png")
                await self._verify_change(before, after, step)
                if step.state:
                    try:
                        self._set_state(WorkflowState(step.state))
                    except ValueError:
                        logger.warning("Unknown state marker on step %s: %s", step_name, step.state)
                if self._session:
                    self._session.completed_steps.append(step_name)
                    self._session.last_screenshot = str(after)
                    self._save_session()
                return
            except Exception as exc:
                fail_shot = self._failure_path(step_name)
                try:
                    after_fail = await self._screenshot(f"fail_{step_name}.png")
                    after_fail.replace(fail_shot)
                except Exception:
                    logger.exception("Could not capture failure screenshot for %s", step_name)
                if step.optional:
                    logger.warning("Optional step %s failed: %s — continuing", step_name, exc)
                    return
                if attempt < self.config.max_retries - 1:
                    wait = min(self.config.retry_delay_s * (2**attempt), 10.0)
                    logger.warning(
                        "Step %s failed (attempt %d/%d): %s — retry in %.1fs",
                        step_name,
                        attempt + 1,
                        self.config.max_retries,
                        exc,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    if self._session:
                        self._session.error = str(exc)
                        self._session.state = WorkflowState.FAILED
                        self._save_session()
                    raise RuntimeError(
                        f"Step '{step_name}' failed after {self.config.max_retries} attempts: {exc}. "
                        f"Failure screenshot: {fail_shot}"
                    ) from exc

    async def _send_shortcut(self, operation: str) -> None:
        keys = VRoidStudioShortcuts.as_hotkey_args(operation)
        if len(keys) == 1 and not VRoidStudioShortcuts.is_modifier_combo(keys):
            result = await keyboard("press", key=keys[0], base_url=self.config.pywinauto_url)
        else:
            result = await keyboard("hotkey", keys=keys, base_url=self.config.pywinauto_url)
        if not result.get("success"):
            raise RuntimeError(result.get("error", f"shortcut failed: {operation}"))

    async def _run_step_action(self, step: StepDef, export_path_holder: dict[str, str]) -> None:
        action = step.action
        if action == "launch":
            result = await self.launch_vroid()
            if not result.get("success"):
                raise RuntimeError(result.get("error", "launch failed"))
            return
        if action == "focus":
            result = await self.focus_vroid()
            if not result.get("success"):
                raise RuntimeError(result.get("error", "focus failed"))
            return
        if action == "wait_stable":
            await self._wait_stable(step.name or "wait")
            return
        if action == "sleep":
            await asyncio.sleep(step.seconds or 1.0)
            return
        if action == "shortcut":
            await self._send_shortcut(step.shortcut or step.name)
            return
        if action == "hotkey":
            result = await keyboard("hotkey", keys=step.keys, base_url=self.config.pywinauto_url)
            if not result.get("success"):
                raise RuntimeError(result.get("error", "hotkey failed"))
            return
        if action == "press":
            result = await keyboard("press", key=step.key, base_url=self.config.pywinauto_url)
            if not result.get("success"):
                raise RuntimeError(result.get("error", "press failed"))
            return
        if action == "type":
            result = await keyboard("type", text=step.text, base_url=self.config.pywinauto_url)
            if not result.get("success"):
                raise RuntimeError(result.get("error", "type failed"))
            return
        if action in ("click", "sample_click"):
            x, y = self._scale_click(step.x, step.y)
            if x is None or y is None:
                raise RuntimeError(f"click step missing coordinates: {step.name}")
            result = await mouse_click(x, y, base_url=self.config.pywinauto_url)
            if not result.get("success"):
                raise RuntimeError(result.get("error", "click failed"))
            return
        if action == "export_vrm":
            await self._send_shortcut("export_vrm")
            await asyncio.sleep(step.seconds or 4.0)
            return
        if action == "export_dialog":
            path = export_path_holder.get("path", "")
            await keyboard("hotkey", keys=["ctrl", "a"], base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.2)
            await keyboard("type", text=path, base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.3)
            await self._send_shortcut("dialog_ok")
            await asyncio.sleep(step.seconds or 6.0)
            return
        if action == "open_file":
            path = step.text or export_path_holder.get("open_path", "")
            if not path:
                raise RuntimeError("open_file step missing open_path")
            await keyboard("hotkey", keys=["ctrl", "a"], base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.2)
            await keyboard("type", text=path, base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.3)
            await self._send_shortcut("dialog_ok")
            await asyncio.sleep(step.seconds or 4.0)
            return
        if action == "save_file":
            path = step.text or export_path_holder.get("save_path", "")
            if not path:
                raise RuntimeError("save_file step missing save_path")
            await keyboard("hotkey", keys=["ctrl", "a"], base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.2)
            await keyboard("type", text=path, base_url=self.config.pywinauto_url)
            await asyncio.sleep(0.3)
            await self._send_shortcut("dialog_ok")
            await asyncio.sleep(step.seconds or 3.0)
            return
        if action == "verify_file":
            path = Path(export_path_holder.get("path", step.path))
            if not path.is_file():
                raise RuntimeError(f"Expected export file missing: {path}")
            return
        if action == "set_export_name":
            return
        raise RuntimeError(f"Unknown step action: {action}")

    async def run_template(
        self,
        template_name: str,
        *,
        open_path: str | None = None,
        save_path: str | None = None,
        export_path: str | None = None,
        session_id: str | None = None,
        resume: bool = False,
    ) -> dict[str, Any]:
        if template_name not in self.catalog.templates:
            return {"success": False, "error": f"Unknown template: {template_name}"}

        holder: dict[str, str] = {}
        if open_path:
            holder["open_path"] = str(Path(open_path).resolve())
        if save_path:
            holder["save_path"] = str(Path(save_path).resolve())
        if export_path:
            holder["path"] = str(Path(export_path).resolve())

        sid = session_id or str(uuid.uuid4())[:8]
        session_path = self.config.session_dir / f"{sid}.json"
        if resume and session_path.is_file():
            self._session = SessionState.from_dict(json.loads(session_path.read_text(encoding="utf-8")))
            self._handle = self._session.handle
        else:
            self._session = SessionState(session_id=sid, archetype_id=f"template:{template_name}")
            self._save_session()

        steps = self.catalog.templates[template_name]
        executed: list[str] = []
        try:
            for step in steps:
                step_name = step.name or step.action
                if resume and step_name in (self._session.completed_steps if self._session else []):
                    continue
                await self._execute_step(step, holder)
                executed.append(step_name)

            if export_path:
                verify = StepDef(action="verify_file", name="verify_export", require_change=False)
                await self._execute_step(verify, holder)

            if self._session:
                self._session.state = WorkflowState.COMPLETE
                self._save_session()

            result: dict[str, Any] = {
                "success": True,
                "template": template_name,
                "session_id": sid,
                "steps_executed": executed,
                "state": WorkflowState.COMPLETE.value,
            }
            if open_path:
                result["open_path"] = holder.get("open_path")
            if save_path:
                result["save_path"] = holder.get("save_path")
            if export_path:
                result["export_path"] = holder.get("path")
            return result
        except Exception as exc:
            logger.exception("Template run failed: %s", template_name)
            return {
                "success": False,
                "template": template_name,
                "session_id": sid,
                "error": str(exc),
                "completed_steps": self._session.completed_steps if self._session else [],
            }

    async def open_project(self, project_path: str) -> dict[str, Any]:
        path = Path(project_path)
        if not path.is_file():
            return {"success": False, "error": f"Project not found: {project_path}"}
        if path.suffix.lower() != ".vroid":
            return {"success": False, "error": f"Expected .vroid project file, got {path.suffix}"}
        return await self.run_template("open_save_only", open_path=str(path.resolve()))

    async def save_project_as(self, save_path: str) -> dict[str, Any]:
        engine_launch = await self.launch_vroid()
        if not engine_launch.get("success"):
            return engine_launch
        await self.focus_vroid()
        holder: dict[str, str] = {"save_path": str(Path(save_path).resolve())}
        steps = [
            StepDef(action="shortcut", name="save_as_dialog", shortcut="save_as", require_change=False),
            StepDef(action="wait_stable", name="save_as_dialog_stable", require_change=False),
            StepDef(action="save_file", name="save_project_path", require_change=False),
        ]
        for step in steps:
            await self._execute_step(step, holder)
        return {"success": True, "save_path": holder["save_path"]}

    async def open_and_export(self, project_path: str, output_name: str) -> dict[str, Any]:
        export_path = str((self.config.output_dir / output_name).resolve())
        return await self.run_template(
            "open_and_export",
            open_path=project_path,
            export_path=export_path,
        )

    async def run_archetype(
        self,
        archetype_id: str,
        *,
        session_id: str | None = None,
        resume: bool = False,
        output_name: str | None = None,
    ) -> dict[str, Any]:
        arch = self.catalog.get(archetype_id)
        export_name = output_name or arch.export_name
        export_path = str((self.config.output_dir / export_name).resolve())
        export_holder = {"path": export_path}

        sid = session_id or str(uuid.uuid4())[:8]
        session_path = self.config.session_dir / f"{sid}.json"

        if resume and session_path.is_file():
            self._session = SessionState.from_dict(json.loads(session_path.read_text(encoding="utf-8")))
            self._handle = self._session.handle
        else:
            self._session = SessionState(session_id=sid, archetype_id=archetype_id)
            self._save_session()

        steps = self.catalog.resolve_steps(archetype_id)
        executed: list[str] = []

        try:
            for step in steps:
                step_name = step.name or step.action
                if step.action == "set_export_name":
                    continue
                if resume and step_name in (self._session.completed_steps if self._session else []):
                    continue
                await self._execute_step(step, export_holder)
                executed.append(step_name)

            verify = StepDef(action="verify_file", name="verify_export", require_change=False)
            await self._execute_step(verify, export_holder)

            self._session.state = WorkflowState.COMPLETE
            self._session.export_path = export_path
            self._save_session()

            size_kb = round(Path(export_path).stat().st_size / 1024, 1)
            return {
                "success": True,
                "archetype_id": archetype_id,
                "display_name": arch.display_name,
                "session_id": sid,
                "export_path": export_path,
                "size_kb": size_kb,
                "steps_executed": executed,
                "state": WorkflowState.COMPLETE.value,
            }
        except Exception as exc:
            logger.exception("Archetype run failed: %s", archetype_id)
            return {
                "success": False,
                "archetype_id": archetype_id,
                "session_id": sid,
                "error": str(exc),
                "state": self._session.state.value if self._session else WorkflowState.FAILED.value,
                "resume_from_step": len(self._session.completed_steps) if self._session else 0,
                "completed_steps": self._session.completed_steps if self._session else [],
            }

    def list_archetypes(self) -> dict[str, Any]:
        items = []
        for arch_id in self.catalog.list_ids():
            arch = self.catalog.get(arch_id)
            items.append(
                {
                    "id": arch_id,
                    "display_name": arch.display_name,
                    "category": arch.category,
                    "template": arch.template,
                    "tags": arch.tags,
                    "export_name": arch.export_name,
                }
            )
        return {
            "success": True,
            "count": len(items),
            "archetypes": items,
        }


def _extract_handle(found: dict[str, Any]) -> int | None:
    result = found.get("result")
    data = getattr(result, "data", None) if result is not None else None
    if isinstance(data, dict) and data.get("handle"):
        return int(data["handle"])
    if isinstance(result, dict):
        inner = result.get("data") or result
        if isinstance(inner, dict) and inner.get("handle"):
            return int(inner["handle"])
    return None
