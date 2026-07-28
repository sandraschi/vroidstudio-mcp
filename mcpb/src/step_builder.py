"""Composable VRoid workflow step fragments — shortcut-first, clicks only for presets."""

from __future__ import annotations

from typing import Any

Step = dict[str, Any]


def _step(
    action: str,
    name: str,
    *,
    shortcut: str = "",
    state: str = "",
    x: int | None = None,
    y: int | None = None,
    seconds: float | None = None,
    require_change: bool = True,
    optional: bool = False,
) -> Step:
    s: Step = {"action": action, "name": name}
    if shortcut:
        s["shortcut"] = shortcut
    if state:
        s["state"] = state
    if x is not None:
        s["x"] = x
    if y is not None:
        s["y"] = y
    if seconds is not None:
        s["seconds"] = seconds
    s["require_change"] = require_change
    if optional:
        s["optional"] = True
    return s


def launch() -> list[Step]:
    return [
        _step("launch", "launch_vroid", state="launched", require_change=False),
        _step("focus", "focus_window", state="focused", require_change=False),
    ]


def new_project() -> list[Step]:
    return [
        _step("shortcut", "new_project", shortcut="new", state="new_project", require_change=False),
        _step("wait_stable", "new_project_stable", require_change=False),
    ]


def pick_sample() -> list[Step]:
    return [
        _step("sample_click", "pick_sample", state="sample_selected"),
        _step("shortcut", "confirm_sample", shortcut="dialog_ok"),
        _step("wait_stable", "model_ready", require_change=False),
    ]


def skip_sample_dialog() -> list[Step]:
    return [
        _step("shortcut", "dismiss_sample", shortcut="dialog_cancel", optional=True, require_change=False),
        _step("wait_stable", "blank_model_ready", require_change=False),
    ]


def editor_tab(shortcut: str, state: str) -> list[Step]:
    return [
        _step("shortcut", state, shortcut=shortcut, state=state, require_change=False),
        _step("wait_stable", f"{state}_stable", require_change=False),
    ]


def preset_click(name: str, x: int, y: int) -> list[Step]:
    return [
        _step("click", name, x=x, y=y),
        _step("wait_stable", f"{name}_applied", require_change=False),
    ]


def save_project() -> list[Step]:
    return [
        _step("shortcut", "save_project", shortcut="save", require_change=False),
        _step("wait_stable", "save_done", require_change=False),
    ]


def save_project_as() -> list[Step]:
    return [
        _step("shortcut", "save_as_dialog", shortcut="save_as", require_change=False),
        _step("wait_stable", "save_as_dialog_stable", require_change=False),
        _step("save_file", "save_project_path", require_change=False),
        _step("wait_stable", "save_as_done", require_change=False),
    ]


def open_project_file() -> list[Step]:
    return [
        _step("shortcut", "open_dialog", shortcut="open", require_change=False),
        _step("wait_stable", "open_dialog_stable", require_change=False),
        _step("open_file", "select_project", state="project_open", require_change=False),
        _step("wait_stable", "project_loaded", require_change=False),
    ]


def export_vrm() -> list[Step]:
    return [
        _step("shortcut", "export_vrm", shortcut="export_vrm", state="exporting", require_change=False),
        _step("sleep", "export_dialog_wait", seconds=5, require_change=False),
        _step("export_dialog", "export_dialog", state="export_dialog", seconds=8, require_change=False),
    ]


def photo_booth_setup() -> list[Step]:
    return [
        _step("shortcut", "photo_booth", shortcut="photo_booth", state="photo_booth", require_change=False),
        _step("wait_stable", "photo_booth_stable", require_change=False),
        _step("shortcut", "front_view", shortcut="front_view", require_change=False),
        _step("shortcut", "zoom_in", shortcut="zoom_in", require_change=False),
        _step("wait_stable", "camera_ready", require_change=False),
    ]


def editor_tour_female() -> list[Step]:
    tabs = [
        ("face_editor", "face_editor"),
        ("hairstyle_editor", "hair_editor"),
        ("body_editor", "body_editor"),
        ("outfits_editor", "outfits_editor"),
        ("accessories_editor", "accessories_editor"),
        ("looks_editor", "looks_editor"),
    ]
    steps: list[Step] = []
    for shortcut, state in tabs:
        steps.extend(editor_tab(shortcut, state))
    return steps


def editor_tour_male() -> list[Step]:
    return editor_tour_female()


def hair_edit_female() -> list[Step]:
    return [
        *editor_tab("hairstyle_editor", "hair_editor"),
        *preset_click("hair_preset", 720, 340),
    ]


def hair_edit_male() -> list[Step]:
    return [
        *editor_tab("hairstyle_editor", "hair_editor"),
        *preset_click("hair_preset", 720, 440),
    ]


def face_edit_female() -> list[Step]:
    return [
        *editor_tab("face_editor", "face_editor"),
        *preset_click("face_preset", 720, 300),
    ]


def face_edit_male() -> list[Step]:
    return [
        *editor_tab("face_editor", "face_editor"),
        *preset_click("face_preset", 720, 400),
    ]


def body_edit_female() -> list[Step]:
    return [
        *editor_tab("body_editor", "body_editor"),
        *preset_click("body_preset", 720, 360),
    ]


def body_edit_male() -> list[Step]:
    return [
        *editor_tab("body_editor", "body_editor"),
        *preset_click("body_preset", 720, 460),
    ]


def outfit_edit_female() -> list[Step]:
    return [
        *editor_tab("outfits_editor", "outfits_editor"),
        *preset_click("outfit_preset", 720, 380),
    ]


def outfit_edit_male() -> list[Step]:
    return [
        *editor_tab("outfits_editor", "outfits_editor"),
        *preset_click("outfit_preset", 720, 480),
    ]


def accessory_edit_female() -> list[Step]:
    return [
        *editor_tab("accessories_editor", "accessories_editor"),
        *preset_click("accessory_preset", 720, 400),
    ]


def compose(*parts: list[Step]) -> list[Step]:
    out: list[Step] = []
    for part in parts:
        out.extend(part)
    return out


def build_templates() -> dict[str, dict[str, list[Step]]]:
    base = lambda *mid: compose(launch(), new_project(), *mid, save_project(), export_vrm())
    sample = pick_sample()

    return {
        "female_sample_minimal": {"steps": base(sample)},
        "female_blank": {"steps": compose(launch(), new_project(), skip_sample_dialog(), save_project(), export_vrm())},
        "female_sample_hair": {"steps": base(sample, hair_edit_female())},
        "female_sample_face": {"steps": base(sample, face_edit_female())},
        "female_sample_body": {"steps": base(sample, body_edit_female())},
        "female_sample_outfit": {"steps": base(sample, outfit_edit_female())},
        "female_sample_accessory": {"steps": base(sample, accessory_edit_female())},
        "female_sample_full": {"steps": base(sample, editor_tour_female())},
        "female_vtuber": {"steps": base(sample, outfit_edit_female(), photo_booth_setup())},
        "female_photo_booth": {"steps": base(sample, photo_booth_setup())},
        "female_editor_tour": {"steps": base(sample, editor_tour_female())},
        "male_sample_minimal": {"steps": base(sample)},
        "male_blank": {"steps": compose(launch(), new_project(), skip_sample_dialog(), save_project(), export_vrm())},
        "male_sample_hair": {"steps": base(sample, hair_edit_male())},
        "male_sample_face": {"steps": base(sample, face_edit_male())},
        "male_sample_body": {"steps": base(sample, body_edit_male())},
        "male_sample_outfit": {"steps": base(sample, outfit_edit_male())},
        "male_sample_full": {"steps": base(sample, editor_tour_male())},
        "male_vtuber": {"steps": base(sample, outfit_edit_male(), photo_booth_setup())},
        "male_photo_booth": {"steps": base(sample, photo_booth_setup())},
        "male_editor_tour": {"steps": base(sample, editor_tour_male())},
        "open_and_export": {
            "steps": compose(launch(), open_project_file(), save_project(), export_vrm()),
        },
        "open_edit_hair_export": {
            "steps": compose(
                launch(),
                open_project_file(),
                hair_edit_female(),
                save_project(),
                export_vrm(),
            ),
        },
        "open_save_only": {
            "steps": compose(launch(), open_project_file(), save_project()),
        },
    }
