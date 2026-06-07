"""Tests for project open workflow step definitions."""

from vroidstudio_mcp.step_builder import build_templates


def test_open_templates_exist():
    templates = build_templates()
    assert "open_and_export" in templates
    assert "open_edit_hair_export" in templates
    assert "open_save_only" in templates


def test_open_and_export_has_open_file_step():
    steps = build_templates()["open_and_export"]["steps"]
    assert any(s.get("action") == "open_file" for s in steps)
