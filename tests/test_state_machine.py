"""Tests for workflow state machine."""

from vroidstudio_mcp.state_machine import SessionState, WorkflowState, can_resume_from, state_index


def test_state_order_progression():
    assert state_index(WorkflowState.FOCUSED) < state_index(WorkflowState.EXPORTING)
    assert state_index(WorkflowState.COMPLETE) > state_index(WorkflowState.NEW_PROJECT)


def test_can_resume_from_saved_state():
    assert can_resume_from(WorkflowState.FOCUSED, WorkflowState.EXPORTING)
    assert not can_resume_from(WorkflowState.FAILED, WorkflowState.FOCUSED)


def test_session_roundtrip():
    session = SessionState("abc123", "quick_gal", state=WorkflowState.HAIR_EDITOR, handle=42)
    session.completed_steps = ["launch_vroid", "focus_window"]
    restored = SessionState.from_dict(session.to_dict())
    assert restored.session_id == "abc123"
    assert restored.state == WorkflowState.HAIR_EDITOR
    assert restored.handle == 42
    assert restored.completed_steps == ["launch_vroid", "focus_window"]
