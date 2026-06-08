# vroidstudio-mcp

VRoid Studio automation via **pywinauto-mcp** — keyboard shortcuts, verified screenshots, calibrated clicks.

No native VRoid API exists. This server drives the GUI with a **state machine** and **55 config-driven archetypes**.

## Ports

| Service | Port |
|---------|------|
| Webapp | 10880 |
| Backend | 10881 |

## Prerequisites

- VRoid Studio installed (`VROIDSTUDIO_PATH`)
- **cua-mcp** (`pywinauto-mcp`) running on **10789** — v0.4.5+ (`automation_assert`, `automation_dialog`, `automation_shortcut`)
- Calibrate `sample_click` coords in `config/archetypes.yaml` or env `VROID_UI_SCALE_X/Y`

### Verification (cua-mcp)

vroidstudio delegates UI stability checks to cua-mcp `automation_assert` (dHash + region masks). Falls back to local SHA256 if cua-mcp is unreachable.

| Env | Default | Purpose |
|-----|---------|---------|
| `VROID_USE_CUA_ASSERT` | `1` | Set `0` to force local hash-only verification |
| `VROID_USE_CUA_DIALOG` | `1` | Set `0` to force local clipboard+keyboard dialog entry |
| `VROID_USE_CUA_SHORTCUT` | `1` | Set `0` to force raw `automation_keyboard` for shortcuts |
| `CUA_MCP_URL` | `http://127.0.0.1:10789` | cua-mcp base URL (alias: `PYWINAUTO_MCP_URL`) |
| `VROID_HASH_ALGORITHM` | `dhash` | Passed to cua-mcp `wait_stable` |
| `VROID_CHANGE_THRESHOLD_PCT` | `1.0` | Min % change for `assert_changed` |
| `VROID_STABLE_REGION_*` | unset | Crop editor canvas (left/top/right/bottom) |

## Start

```powershell
.\start.ps1
```

## Architecture

```text
vroid_studio MCP tool
  -> AutomationEngine (state machine + verification)
    -> pywinauto-mcp HTTP (:10789)
      -> VRoid Studio GUI
```

### Resilience

- Every step: screenshot before/after, wait-for-stable UI (hash polling)
- Failures: timestamped PNG in `{work_dir}/failures/`
- Resume: `run_archetype` with `resume=true` and `session_id`

### Configuration

| File | Purpose |
|------|---------|
| `src/vroidstudio_mcp/step_builder.py` | **Source of truth** for step templates (shortcut-first) |
| `scripts/build_defaults_yaml.py` | Regenerate `config/defaults.yaml` from step_builder |
| `scripts/generate_archetypes.py` | Regenerate 55 archetype definitions |
| `config/archetypes.yaml` | Archetype → template mapping + sample clicks |

After editing templates:

```powershell
uv run python scripts/build_defaults_yaml.py
uv run python scripts/generate_archetypes.py
```

### Template types (21)

| Template | Flow |
|----------|------|
| `female/male_sample_minimal` | launch → new → sample → save → F8 export |
| `female/male_sample_{hair,face,body,outfit,accessory}` | + F1–F5 tab + preset click |
| `female/male_sample_full` | + F1–F6 editor tour |
| `female/male_editor_tour` | F1–F6 tour + save + export (VRChat archetypes) |
| `female/male_vtuber` | outfit edit + F7 photo booth + camera shortcuts |
| `female/male_photo_booth` | F7 + front_view + zoom_in |
| `female/male_blank` | new project, skip sample, export |

Clicks are **only** used for sample-model tile and preset thumbnails. Everything else uses `VRoidStudioShortcuts`.

## MCP tool: `vroid_studio`

| Operation | Description |
|-----------|-------------|
| `status` | Window + outputs + archetype count |
| `launch` | Start VRoid Studio |
| `focus` | Focus main window |
| `screenshot` | Debug PNG |
| `list_archetypes` | All 55 archetypes |
| `run_archetype` | Run named archetype (`archetype_id`, `resume`, `session_id`) |
| `session_status` | Inspect persisted session |
| `quick_gal_export` | Legacy fleet alias → `quick_gal` archetype |
| `list_outputs` | Exported VRM files |
| `open_project` | Open `.vroid` in Studio (Ctrl+O automation) |
| `save_project` | Ctrl+S save current project |
| `save_project_as` | Save `.vroid` copy to `save_path` |
| `open_and_export` | Open `.vroid` → save → F8 export VRM |
| `run_template` | Run named template (`open_edit_hair_export`, etc.) |

## Archetype categories (55)

| Category | Count |
|----------|-------|
| female_anime | 15 |
| male_anime | 12 |
| female_realistic | 5 |
| male_realistic | 5 |
| stylized | 5 |
| vtuber | 5 |
| seasonal | 5 |
| fleet (quick_gal, blanks) | 3 |

## Fleet pipeline

Part of the avatar creative chain orchestrated by **avatar-mcp**. See [docs/PIPELINE.md](docs/PIPELINE.md).

## Keyboard shortcuts

See `src/vroidstudio_mcp/keyboard_shortcuts.py` — F1–F6 editors, F8 export, Ctrl+N new project.
