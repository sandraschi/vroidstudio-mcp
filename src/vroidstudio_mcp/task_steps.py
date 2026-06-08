"""Convert VRoid StepDef sequences to cua-mcp automation_task step JSON."""

from __future__ import annotations

from typing import Any, Callable

from vroidstudio_mcp.archetypes import StepDef

TaskStep = dict[str, Any]

_SKIP_ACTIONS = frozenset({"launch", "set_export_name"})
_LOCAL_ONLY = frozenset({"hotkey", "press", "type"})


def step_defs_to_task_steps(
    steps: list[StepDef],
    holder: dict[str, str],
    *,
    scale_click: Callable[[int | None, int | None], tuple[int | None, int | None]] | None = None,
    stable_frames_required: int = 3,
    stable_timeout_s: float = 15.0,
) -> tuple[list[TaskStep], list[StepDef]]:
    """Map catalog steps to automation_task steps; return (task_steps, hybrid_steps)."""
    task_steps: list[TaskStep] = []
    hybrid: list[StepDef] = []

    for step in steps:
        if step.action in _SKIP_ACTIONS:
            continue
        if step.action in _LOCAL_ONLY:
            hybrid.append(step)
            continue

        converted = _convert_one(
            step,
            holder,
            scale_click=scale_click,
            stable_frames_required=stable_frames_required,
            stable_timeout_s=stable_timeout_s,
        )
        if converted is None:
            hybrid.append(step)
        elif isinstance(converted, list):
            task_steps.extend(converted)
        else:
            task_steps.append(converted)

    return task_steps, hybrid


def verify_export_task_step(export_path: str) -> TaskStep:
    return {
        "name": "verify_export",
        "kind": "assert_file",
        "path": export_path,
        "check": "file_exists",
        "on_fail": "abort",
    }


def _on_fail(step: StepDef) -> str:
    if step.optional:
        return "abort"
    return "refocus_retry"


def _convert_one(
    step: StepDef,
    holder: dict[str, str],
    *,
    scale_click: Callable[[int | None, int | None], tuple[int | None, int | None]] | None,
    stable_frames_required: int,
    stable_timeout_s: float,
) -> TaskStep | list[TaskStep] | None:
    name = step.name or step.action
    base: TaskStep = {"name": name, "on_fail": _on_fail(step)}
    if step.optional:
        base["optional"] = True

    action = step.action
    if action == "focus":
        return {**base, "kind": "focus"}

    if action == "wait_stable":
        return {
            **base,
            "kind": "wait_stable",
            "stable_frames_required": stable_frames_required,
            "timeout_s": stable_timeout_s,
        }

    if action == "sleep":
        return {**base, "kind": "sleep", "seconds": float(step.seconds or 1.0)}

    if action == "shortcut":
        return {
            **base,
            "kind": "shortcut",
            "app": "vroidstudio",
            "action": step.shortcut or step.name,
            "verify_stable": step.require_change,
        }

    if action in ("click", "sample_click"):
        x, y = (step.x, step.y)
        if scale_click:
            x, y = scale_click(step.x, step.y)
        if x is None or y is None:
            return None
        return {**base, "kind": "click", "x": int(x), "y": int(y)}

    if action == "export_vrm":
        return [
            {
                **base,
                "kind": "shortcut",
                "app": "vroidstudio",
                "action": "export_vrm",
                "verify_stable": False,
            },
            {
                "name": f"{name}_wait",
                "kind": "sleep",
                "seconds": float(step.seconds or 4.0),
                "on_fail": "retry",
            },
        ]

    if action == "export_dialog":
        path = holder.get("path", "")
        if not path:
            return None
        return {
            **base,
            "kind": "dialog",
            "path": path,
            "use_clipboard": True,
            "post_confirm_pause_s": float(step.seconds or 6.0),
        }

    if action == "open_file":
        path = step.text or holder.get("open_path", "")
        if not path:
            return None
        return {
            **base,
            "kind": "dialog",
            "path": path,
            "use_clipboard": True,
            "post_confirm_pause_s": float(step.seconds or 4.0),
        }

    if action == "save_file":
        path = step.text or holder.get("save_path", "")
        if not path:
            return None
        return {
            **base,
            "kind": "dialog",
            "path": path,
            "use_clipboard": True,
            "post_confirm_pause_s": float(step.seconds or 3.0),
        }

    if action == "verify_file":
        path = holder.get("path", step.path)
        if not path:
            return None
        return {**base, "kind": "assert_file", "path": path, "check": "file_exists"}

    return None
