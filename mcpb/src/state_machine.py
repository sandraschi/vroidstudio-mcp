"""Explicit workflow states for VRoid Studio automation."""

from __future__ import annotations

from enum import Enum
from typing import Any


class WorkflowState(str, Enum):
    IDLE = "idle"
    LAUNCHING = "launching"
    LAUNCHED = "launched"
    FOCUSED = "focused"
    NEW_PROJECT = "new_project"
    SAMPLE_SELECTED = "sample_selected"
    FACE_EDITOR = "face_editor"
    HAIR_EDITOR = "hair_editor"
    BODY_EDITOR = "body_editor"
    OUTFITS_EDITOR = "outfits_editor"
    ACCESSORIES_EDITOR = "accessories_editor"
    LOOKS_EDITOR = "looks_editor"
    PHOTO_BOOTH = "photo_booth"
    EXPORTING = "exporting"
    EXPORT_DIALOG = "export_dialog"
    COMPLETE = "complete"
    FAILED = "failed"


# Ordered progression for resume logic
STATE_ORDER: list[WorkflowState] = [
    WorkflowState.IDLE,
    WorkflowState.LAUNCHING,
    WorkflowState.LAUNCHED,
    WorkflowState.FOCUSED,
    WorkflowState.NEW_PROJECT,
    WorkflowState.SAMPLE_SELECTED,
    WorkflowState.FACE_EDITOR,
    WorkflowState.HAIR_EDITOR,
    WorkflowState.BODY_EDITOR,
    WorkflowState.OUTFITS_EDITOR,
    WorkflowState.ACCESSORIES_EDITOR,
    WorkflowState.LOOKS_EDITOR,
    WorkflowState.PHOTO_BOOTH,
    WorkflowState.EXPORTING,
    WorkflowState.EXPORT_DIALOG,
    WorkflowState.COMPLETE,
]


def state_index(state: WorkflowState) -> int:
    try:
        return STATE_ORDER.index(state)
    except ValueError:
        return -1


def can_resume_from(saved: WorkflowState, target: WorkflowState) -> bool:
    if saved == WorkflowState.FAILED:
        return False
    return state_index(saved) <= state_index(target)


class SessionState:
    """Persisted session for resume-from-last-good-state."""

    def __init__(
        self,
        session_id: str,
        archetype_id: str,
        *,
        state: WorkflowState = WorkflowState.IDLE,
        handle: int | None = None,
        completed_steps: list[str] | None = None,
        last_screenshot: str | None = None,
        export_path: str | None = None,
        error: str | None = None,
        last_task_id: str | None = None,
    ) -> None:
        self.session_id = session_id
        self.archetype_id = archetype_id
        self.state = state
        self.handle = handle
        self.completed_steps = completed_steps or []
        self.last_screenshot = last_screenshot
        self.export_path = export_path
        self.error = error
        self.last_task_id = last_task_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "archetype_id": self.archetype_id,
            "state": self.state.value,
            "handle": self.handle,
            "completed_steps": self.completed_steps,
            "last_screenshot": self.last_screenshot,
            "export_path": self.export_path,
            "error": self.error,
            "last_task_id": self.last_task_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionState:
        return cls(
            session_id=str(data["session_id"]),
            archetype_id=str(data["archetype_id"]),
            state=WorkflowState(data.get("state", WorkflowState.IDLE.value)),
            handle=data.get("handle"),
            completed_steps=list(data.get("completed_steps") or []),
            last_screenshot=data.get("last_screenshot"),
            export_path=data.get("export_path"),
            error=data.get("error"),
            last_task_id=data.get("last_task_id"),
        )
