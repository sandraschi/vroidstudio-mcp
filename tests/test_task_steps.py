"""Tests for StepDef → automation_task conversion."""

from vroidstudio_mcp.archetypes import StepDef
from vroidstudio_mcp.task_steps import step_defs_to_task_steps, verify_export_task_step


def test_shortcut_and_dialog_conversion():
    holder = {"path": r"D:\out\model.vrm"}
    steps = [
        StepDef(action="focus", name="focus_window", require_change=False),
        StepDef(action="shortcut", name="new_project", shortcut="new", require_change=True),
        StepDef(action="export_dialog", name="export_path", seconds=5.0, require_change=False),
    ]
    task_steps, hybrid = step_defs_to_task_steps(steps, holder)
    assert hybrid == []
    assert len(task_steps) == 3
    assert task_steps[0]["kind"] == "focus"
    assert task_steps[1]["kind"] == "shortcut"
    assert task_steps[1]["action"] == "new"
    assert task_steps[2]["kind"] == "dialog"
    assert task_steps[2]["path"] == holder["path"]
    assert task_steps[2]["post_confirm_pause_s"] == 5.0


def test_export_vrm_expands_to_shortcut_and_sleep():
    steps = [StepDef(action="export_vrm", name="export", seconds=3.0)]
    task_steps, _ = step_defs_to_task_steps(steps, {})
    assert len(task_steps) == 2
    assert task_steps[0]["kind"] == "shortcut"
    assert task_steps[0]["action"] == "export_vrm"
    assert task_steps[1]["kind"] == "sleep"
    assert task_steps[1]["seconds"] == 3.0


def test_click_scaled_and_hybrid_fallback():
    scaled = []

    def scale(x, y):
        scaled.append((x, y))
        return (x * 2 if x else None, y * 2 if y else None)

    steps = [
        StepDef(action="click", name="pick", x=100, y=200),
        StepDef(action="hotkey", name="legacy", keys=["ctrl", "s"]),
    ]
    task_steps, hybrid = step_defs_to_task_steps(steps, {}, scale_click=scale)
    assert scaled == [(100, 200)]
    assert task_steps[0]["kind"] == "click"
    assert task_steps[0]["x"] == 200
    assert task_steps[0]["y"] == 400
    assert len(hybrid) == 1
    assert hybrid[0].action == "hotkey"


def test_verify_export_step():
    step = verify_export_task_step(r"C:\tmp\out.vrm")
    assert step["kind"] == "assert_file"
    assert step["path"] == r"C:\tmp\out.vrm"
