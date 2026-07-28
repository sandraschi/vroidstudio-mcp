"""VRoid Studio keyboard shortcuts — preferred over brittle UI clicks.

Official reference:
https://vroid.pixiv.help/hc/en-us/articles/900006050066
"""

from __future__ import annotations

from typing import ClassVar

SHORTCUTS_DOCUMENTATION_URL = "https://vroid.pixiv.help/hc/en-us/articles/900006050066"


class VRoidStudioShortcuts:
    # File
    SAVE = "ctrl+s"
    SAVE_AS = "ctrl+shift+s"
    OPEN = "ctrl+o"
    NEW = "ctrl+n"
    UNDO = "ctrl+z"
    REDO = "ctrl+shift+z"

    # Editor tabs (F-keys)
    FACE_EDITOR = "f1"
    HAIRSTYLE_EDITOR = "f2"
    BODY_EDITOR = "f3"
    OUTFITS_EDITOR = "f4"
    ACCESSORIES_EDITOR = "f5"
    LOOKS_EDITOR = "f6"
    PHOTO_BOOTH = "f7"
    EXPORT_VRM = "f8"
    UPLOAD_TO_VROID_HUB = "f9"

    # Preset panels
    PRESET_TAB = "ctrl+1"
    CUSTOM_TAB = "ctrl+2"

    # Camera
    FRONT_VIEW = "1"
    TILT_DOWN_15 = "2"
    FRONT_RIGHT_VIEW = "3"
    ROTATE_LEFT_15 = "4"
    TOGGLE_PROJECTION = "5"
    ROTATE_RIGHT_15 = "6"
    TOP_VIEW = "7"
    TILT_UP_15 = "8"
    INVERT_VIEW = "9"

    # Zoom
    ZOOM_IN = "ctrl+;"
    ZOOM_OUT = "ctrl+-"

    # Hair editor tools
    SELECT_TOOL = "v"
    BRUSH_TOOL = "b"
    RETOUCH_BRUSH_TOOL = "f"
    CONTROL_POINT_TOOL = "c"
    TOGGLE_MOVE_GIZMO = "w"
    TOGGLE_ROTATE_GIZMO = "e"
    TOGGLE_SCALE_GIZMO = "r"
    DELETE_HAIR = "ctrl+backspace"
    SMOOTHING = "s"

    # Texture editor
    TEXTURE_ERASER_TOOL = "e"
    TEXTURE_BUCKET_TOOL = "g"
    TEXTURE_BLUR_TOOL = "r"
    COLOR_PICKER = "alt"
    BRUSH_SIZE_DECREASE = "]"
    BRUSH_SIZE_INCREASE = "["
    DELETE_LAYER = "delete"
    DUPLICATE_LAYER = "ctrl+d"
    HIDE_LAYER = "ctrl+h"
    RENAME_LAYER = "ctrl+r"
    LOCK_LAYER = "ctrl+l"
    IMPORT_LAYER = "ctrl+shift+i"
    EXPORT_LAYER = "ctrl+shift+e"
    MOVE_LAYER_UP = "ctrl+]"
    MOVE_LAYER_DOWN = "ctrl+["
    MERGE_LAYERS = "ctrl+e"
    OUTFIT_TEXTURE_BRUSH_PANEL = "ctrl+9"
    OUTFIT_TEXTURE_PARAMETERS_PANEL = "ctrl+0"

    # Accessory editor
    SWITCH_GIZMO_AXES = "x"

    # Dialogs
    DIALOG_OK = "enter"
    DIALOG_CANCEL = "escape"
    DIALOG_TAB_NEXT = "tab"
    DIALOG_TAB_PREV = "shift+tab"

    _MAP: ClassVar[dict[str, str]] = {
        "save": SAVE,
        "save_as": SAVE_AS,
        "open": OPEN,
        "new": NEW,
        "undo": UNDO,
        "redo": REDO,
        "face_editor": FACE_EDITOR,
        "hairstyle_editor": HAIRSTYLE_EDITOR,
        "body_editor": BODY_EDITOR,
        "outfits_editor": OUTFITS_EDITOR,
        "accessories_editor": ACCESSORIES_EDITOR,
        "looks_editor": LOOKS_EDITOR,
        "photo_booth": PHOTO_BOOTH,
        "export_vrm": EXPORT_VRM,
        "upload_to_vroid_hub": UPLOAD_TO_VROID_HUB,
        "preset_tab": PRESET_TAB,
        "custom_tab": CUSTOM_TAB,
        "front_view": FRONT_VIEW,
        "tilt_down_15": TILT_DOWN_15,
        "front_right_view": FRONT_RIGHT_VIEW,
        "rotate_left_15": ROTATE_LEFT_15,
        "toggle_projection": TOGGLE_PROJECTION,
        "rotate_right_15": ROTATE_RIGHT_15,
        "top_view": TOP_VIEW,
        "tilt_up_15": TILT_UP_15,
        "invert_view": INVERT_VIEW,
        "zoom_in": ZOOM_IN,
        "zoom_out": ZOOM_OUT,
        "select_tool": SELECT_TOOL,
        "brush_tool": BRUSH_TOOL,
        "retouch_brush_tool": RETOUCH_BRUSH_TOOL,
        "control_point_tool": CONTROL_POINT_TOOL,
        "toggle_move_gizmo": TOGGLE_MOVE_GIZMO,
        "toggle_rotate_gizmo": TOGGLE_ROTATE_GIZMO,
        "toggle_scale_gizmo": TOGGLE_SCALE_GIZMO,
        "delete_hair": DELETE_HAIR,
        "smoothing": SMOOTHING,
        "texture_eraser_tool": TEXTURE_ERASER_TOOL,
        "texture_bucket_tool": TEXTURE_BUCKET_TOOL,
        "texture_blur_tool": TEXTURE_BLUR_TOOL,
        "color_picker": COLOR_PICKER,
        "brush_size_decrease": BRUSH_SIZE_DECREASE,
        "brush_size_increase": BRUSH_SIZE_INCREASE,
        "delete_layer": DELETE_LAYER,
        "duplicate_layer": DUPLICATE_LAYER,
        "hide_layer": HIDE_LAYER,
        "rename_layer": RENAME_LAYER,
        "lock_layer": LOCK_LAYER,
        "import_layer": IMPORT_LAYER,
        "export_layer": EXPORT_LAYER,
        "move_layer_up": MOVE_LAYER_UP,
        "move_layer_down": MOVE_LAYER_DOWN,
        "merge_layers": MERGE_LAYERS,
        "outfit_texture_brush_panel": OUTFIT_TEXTURE_BRUSH_PANEL,
        "outfit_texture_parameters_panel": OUTFIT_TEXTURE_PARAMETERS_PANEL,
        "switch_gizmo_axes": SWITCH_GIZMO_AXES,
        "dialog_ok": DIALOG_OK,
        "dialog_cancel": DIALOG_CANCEL,
        "dialog_tab_next": DIALOG_TAB_NEXT,
        "dialog_tab_prev": DIALOG_TAB_PREV,
        "export": EXPORT_VRM,
    }

    @classmethod
    def get(cls, operation: str) -> str | None:
        return cls._MAP.get(operation.lower())

    @classmethod
    def list_all(cls) -> dict[str, str]:
        return dict(cls._MAP)

    @classmethod
    def parse_hotkey(cls, shortcut: str) -> list[str]:
        return [part.strip() for part in shortcut.lower().split("+") if part.strip()]

    @classmethod
    def as_hotkey_args(cls, operation: str) -> list[str]:
        shortcut = cls.get(operation)
        if not shortcut:
            raise KeyError(f"Unknown VRoid shortcut operation: {operation}")
        return cls.parse_hotkey(shortcut)

    @classmethod
    def is_function_key(cls, key: str) -> bool:
        k = key.lower()
        return k.startswith("f") and k[1:].isdigit()

    @classmethod
    def is_modifier_combo(cls, keys: list[str]) -> bool:
        mods = {"ctrl", "shift", "alt", "win"}
        return len(keys) > 1 and any(k in mods for k in keys)
