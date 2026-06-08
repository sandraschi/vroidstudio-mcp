"""Tests for cua-mcp HTTP client helpers."""

from vroidstudio_mcp.pywinauto_client import parse_tool_result


def test_parse_tool_result_direct_dict():
    raw = {"status": "success", "message": "ok", "data": {"hash": "abc"}}
    assert parse_tool_result(raw)["data"]["hash"] == "abc"


def test_parse_tool_result_json_text_block():
    raw = [{"type": "text", "text": '{"status": "success", "message": "stable", "data": {"stable": true}}'}]
    parsed = parse_tool_result(raw)
    assert parsed["status"] == "success"
    assert parsed["data"]["stable"] is True


def test_parse_tool_result_nested_result():
    raw = {"result": {"status": "error", "message": "timeout", "recovery_tip": "retry"}}
    assert parse_tool_result(raw)["recovery_tip"] == "retry"
