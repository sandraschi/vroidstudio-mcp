"""Tests for composable step templates."""

from vroidstudio_mcp.step_builder import build_templates


def test_template_count():
    templates = build_templates()
    assert len(templates) == 24


def test_open_project_template_uses_shortcuts():
    steps = build_templates()["open_and_export"]["steps"]
    names = [s["name"] for s in steps]
    assert "open_dialog" in names
    assert "select_project" in names
    assert "save_project" in names
    assert "export_vrm" in names


def test_full_tour_uses_shortcuts():
    steps = build_templates()["female_editor_tour"]["steps"]
    shortcuts = [s for s in steps if s["action"] == "shortcut"]
    assert any(s.get("shortcut") == "face_editor" for s in shortcuts)
    assert any(s.get("shortcut") == "looks_editor" for s in shortcuts)
    assert any(s.get("shortcut") == "save" for s in shortcuts)
    assert any(s.get("shortcut") == "export_vrm" for s in shortcuts)


def test_vtuber_includes_photo_booth():
    steps = build_templates()["female_vtuber"]["steps"]
    names = [s["name"] for s in steps]
    assert "photo_booth" in names
    assert "front_view" in names
    assert "zoom_in" in names


def test_clicks_only_for_presets_and_sample():
    for name, body in build_templates().items():
        if "blank" in name:
            continue
        clicks = [s for s in body["steps"] if s["action"] in ("click", "sample_click")]
        for c in clicks:
            assert c["name"] in ("pick_sample", "hair_preset", "face_preset", "body_preset", "outfit_preset", "accessory_preset")
