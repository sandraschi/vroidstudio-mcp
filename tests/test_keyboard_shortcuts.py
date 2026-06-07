"""Tests for VRoid keyboard shortcut catalog."""

from vroidstudio_mcp.keyboard_shortcuts import SHORTCUTS_DOCUMENTATION_URL, VRoidStudioShortcuts


def test_shortcut_map_has_editor_tabs():
    shortcuts = VRoidStudioShortcuts.list_all()
    assert shortcuts["face_editor"] == "f1"
    assert shortcuts["export_vrm"] == "f8"
    assert shortcuts["upload_to_vroid_hub"] == "f9"
    assert len(shortcuts) >= 50


def test_parse_hotkey():
    assert VRoidStudioShortcuts.parse_hotkey("ctrl+shift+s") == ["ctrl", "shift", "s"]
    assert VRoidStudioShortcuts.as_hotkey_args("save") == ["ctrl", "s"]


def test_documentation_url():
    assert "pixiv.help" in SHORTCUTS_DOCUMENTATION_URL
