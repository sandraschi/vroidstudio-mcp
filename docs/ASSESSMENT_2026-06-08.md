# vroidstudio-mcp — Assessment & TODO
**Date:** 2026-06-08 (rev 2 — full source audit)
**Version assessed:** 0.3.6 (local; pushed: 0.3.5)
**Dependency:** cua-mcp @ 10789, system-admin-mcp @ 10861
**Fleet spec mirror:** pywinauto-mcp [TARGETS_PAGE_SKETCH.md](../../pywinauto-mcp/docs/TARGETS_PAGE_SKETCH.md)

---

## Reconciliation (Cursor, 2026-06-08)

| ID | Original claim | Reconciled status |
|----|----------------|-------------------|
| Critical 1 | cua-mcp tools may not register | **Closed** — tools register; failures were `structured_content` parse + slow UIA find (fixed in cua-mcp + `pywinauto_client.py`) |
| V1 | Migrate to `automation_task` | **Done** v0.3.4–0.3.5 — `task_steps.py`, `_run_catalog_via_task`, resume filter |
| V2 | VRoid template library | **Done in cua-mcp** v0.5.3 — placeholders only; real captures still needed |
| Critical 3 | Sample click uncalibrated | **Confirmed** — live `quick_gal` failed at `assert_file`; VRoid 2.3.0 @ `%LOCALAPPDATA%\Programs\VRoidStudio\2.3.0\` |
| Critical 2 | Preflight missing cua tool check | **Open** — add `list_profiles` / tool manifest probe |
| V3 | `health_check` operation | **Open** — high value next |
| V7 | Webapp live session monitor | **Spec in cua-mcp** W1 / [TARGETS_PAGE_SKETCH.md](../../pywinauto-mcp/docs/TARGETS_PAGE_SKETCH.md) |

**Local fixes not yet pushed:** VRoid path auto-detect, `structured_content` parser, HWND from `windows[]`, smoke scripts.

---

## What This Actually Is

vroidstudio-mcp is a specialised orchestration layer on top of cua-mcp, not a general automation server. Its value proposition is the 55 YAML-driven archetypes and the `AutomationEngine` state machine — it knows the VRoid Studio workflow in detail so callers don't have to. It is also the primary real-world test subject for cua-mcp's CUA primitives: every hard problem in cua-mcp (GPU rendering noise, Unity foreground requirement, dialog brittleness, sample picker coordinates) was discovered through VRoid.

The architecture has a natural tension: as cua-mcp matures (`automation_task`, `shortcut_engine`, `dialog_engine`, `automation_assert`), vroidstudio-mcp's own `AutomationEngine` and `step_builder` are reimplementing the same machinery at a higher, VRoid-specific level. The right end state is vroidstudio-mcp as a thin config+archetype layer over `automation_task`, not its own parallel state machine. That migration is worth planning now even if it takes several sessions to complete.

---

## Issues & TODO

### Critical

**1. ~~cua-mcp tools may not register~~ → CLOSED.** Root cause was HTTP response shape (`structured_content`) and slow `automation_windows find`, not missing registration. Keep explicit preflight tool-list check (item 2).

**2. `preflight.py` does not verify cua-mcp tool availability.**
It should call `automation_system("help")` or `automation_task(operation="list_profiles")` at startup and log warnings if `automation_assert` / `automation_shortcut` / `automation_dialog` are missing from the response. Right now a misconfigured cua-mcp is indistinguishable from a correctly falling-back vroidstudio-mcp.

**3. Sample model click coordinates `VROID_SAMPLE_MODEL_X/Y` are resolution-dependent and have no calibration check.**
Defaults are not visible in server.py (they live in `config.py` or `archetypes.yaml`). On a display with non-1080p or non-100% DPI these silently miss. No test validates them at startup. Fix: cua-mcp F9 (preset grid mapping via template match) is the right solution; interim fix is a preflight screenshot + warn if the sample picker template is not visible at the configured coordinates.

### High Priority

**4. `webapp/` and `web_sota/` both exist with committed `dist/` directories — unclear which one `start.ps1` serves.**
Read `start.ps1` to determine which port/directory is actually started. Whichever one is active: remove the other, add `dist/` to `.gitignore`, add `bun install && bun run build` to the start script.

**5. `sysadmin_client.py` is a local copy of pywinauto-mcp's `sysadmin_client.py`.**
Any fix applied to cua-mcp's version will not propagate here. Options: (a) import directly from `pywinauto_mcp.sysadmin_client` since it's a dependency, (b) if the content has diverged, document why. Sync or remove.

**6. Smoke tests (`scripts/run_smoke_export.py`, `scripts/smoke_e2e.py`) not wired to CI.**
The most valuable tests for this repo are the end-to-end ones that actually try to export from VRoid. They need a `requires_hardware` / `requires_vroid` marker (same pattern as cua-mcp's `requires_hardware`) so CI skips them but local runs execute them. Add `docs/TESTING.md` explaining this.

**7. No `CHANGELOG.md`.**
Fleet standard. Add one. Minimum: list the major changes Cursor made in this session.

### Medium Priority

**8. `config/archetypes.yaml` (repo root) duplicates `src/vroidstudio_mcp/config/archetypes.yaml`.**
`VRoidStudioConfig` reads from the `src/` path (bundled via `package-data`). The repo-root copy is unused dead weight and will diverge. Delete `config/` at root or replace it with a symlink/comment pointing to the real location.

**9. `AutomationEngine._execute_step()` in `automation.py` has its own wait_stable / verify logic.**
This is the duplication vector. As cua-mcp's `automation_assert(wait_stable)` matures, `AutomationEngine` should delegate to it rather than maintaining parallel hash logic. Not urgent now — but each session that improves `AutomationEngine` in isolation widens the gap with cua-mcp. Add a comment marking the duplication so Cursor doesn't reinforce it.

**10. `step_builder.py` is the source of truth for 21 template types but is not documented inline.**
Each template should have a one-line comment describing its flow. Currently Cursor must infer intent from the step sequence. This matters because step_builder is the primary input to the archetype generator — a wrong assumption here generates 55 wrong archetypes.

**11. `test_project_workflows.py` — confirm it doesn't have test-order dependencies via the shared `_get_engine()` global.**
`AutomationEngine` is a module-level singleton. Tests that call `_get_engine()` may share state. Add `autouse` fixture that resets `_engine = None` between tests.

**12. `pywinauto_client.py` operation strings — confirm they match cua-mcp's actual registered tool operation names.**
The wrapper calls things like `windows("find", ...)`, `keyboard("hotkey", ...)`. If cua-mcp's portmanteau uses different operation name strings (e.g. `automation_windows("find")` expects `operation="find"` as first positional), mismatches produce `{"success": False, "error": "Unknown operation"}` that may look like a VRoid state issue rather than a wiring issue.

### Low Priority

**13. `scripts/FleetStartMode.ps1` — purpose unclear. Document or delete.**

**14. `web_sota/start.ps1.bak.*` (two files from 2026-05-08). Delete.**

**15. `docs/PIPELINE.md` references `avatar-mcp (10793)` and `blender-mcp (10849)`. Verify ports are current in WEBAPP_PORTS.md.**

**16. README archetype count "55" should be a generated value, not a hardcoded string. Add assertion in `test_archetypes.py`: `assert len(archetypes) == EXPECTED_COUNT`.**

---

## Feature Suggestions for Cursor

vroidstudio-mcp is the best test subject in the fleet for CUA primitives because VRoid is hard: Unity/GPU rendering (non-deterministic screenshots), foreground-only input, no UIA tree for most controls, modal dialogs, slow operations (model loading, hair physics, export), and a rich enough workflow to exercise every cua-mcp feature.

### V1 — ~~Migrate to automation_task~~ → DONE (v0.3.4–0.3.5)
`task_steps.py`, `_run_catalog_via_task()`, resume via `filter_completed_task_steps`. Hybrid fallback remains for `hotkey`/`press`/`type`. Next: retire local `_wait_stable` when `VROID_USE_CUA_TASK=1` is always on.

### V2 — VRoid Template Library (half day, but high value)
**Captured PNGs that make assert_template actually work.**

Take screenshots of VRoid Studio at standard resolution and extract these regions:
- `export_dialog_title` — the "Export as VRM" dialog header
- `sample_picker_visible` — the sample model grid (confirms new-project landed on picker screen)
- `save_confirm_dialog` — the overwrite confirm dialog
- `f8_progress_bar` — export progress indicator (for wait_stable region masking)
- `editor_hair_tab_active` — F1 editor active state
- `editor_face_tab_active` — F2 active state
- `photo_booth_visible` — F7 photo booth open

Commit to `src/pywinauto_mcp/templates/vroidstudio/default/` (cua-mcp's template library). Update `manifest.yaml`. These enable `assert_template` steps in every archetype.

### V3 — VRoid Health Check Tool Operation (half day)
**A fast triage operation before running an archetype.**

`vroid_studio(operation="health_check")` that:
1. Checks VRoid process running (status op already does this)
2. Calls cua-mcp preflight (disk, memory)
3. Takes a screenshot and checks: is the main window visible? Is it the expected size? Can we see the editor toolbar (template match)?
4. Reports: `{"healthy": bool, "issues": [...], "screenshot_path": "..."}` with a base64 thumbnail

Saves a lot of failed archetype runs from bad initial state. Currently the only way to check is `status` (which only checks window handle) or running an archetype and watching it fail.

### V4 — Per-Archetype Dry Run Mode (1 day)
**Makes archetype development and debugging much faster.**

`vroid_studio(operation="run_archetype", archetype_id="quick_gal", dry_run=True)` that:
1. Resolves the archetype → template → step list
2. Logs each step that would be executed with its parameters
3. Takes a screenshot at the start and annotates which coordinates/shortcuts would fire
4. Does NOT send any input to VRoid

Makes it possible to verify an archetype's step list is correct without actually running VRoid Studio, and to debug coordinate issues without causing VRoid state changes.

### V5 — Session Replay from JSONL (1 day)
**Connects vroidstudio-mcp sessions to cua-mcp's mission_store.**

When `run_archetype` executes, write each step to `mission_store.record_step(session_id, step)`. This gives:
- `vroid_studio(operation="replay", session_id="...")` to re-run a successful export on a different project file
- Persistent session JSONL that can be inspected after crashes
- Foundation for macro recording: run an archetype once, save the JSONL, replay it unchanged or with different project_path / output_name params

`mission_store.py` already exists in cua-mcp and supports this — it just needs to be called from `AutomationEngine`.

### V6 — VRoid Archetype Parameterisation (1 day)
**Makes archetypes more flexible without multiplying their count.**

Currently "female_anime_hair_preset_01" through "female_anime_hair_preset_15" differ only in which preset is clicked. Replace with a parameterised call:

`vroid_studio(operation="run_archetype", archetype_id="female_anime_hair", params={"preset_index": 3})`

The archetype YAML gets a `params_schema` block. `step_builder` substitutes params at runtime. This collapses many near-duplicate archetypes into fewer parameterised ones, makes the 55-archetype count honest, and makes it easier to add new presets without regenerating YAML.

### V7 — VRoid Webapp Live Session Monitor (1 day)
**Makes the webapp actually useful during long exports.**

The current webapp has a `VroidPage.tsx` with presumably status + controls. Extend it to show:
- Live session step progress (poll `/api/v1/control/tool` `session_status` every 2s)
- Current step name and index / total
- Before/after screenshots from evidence (load from `/api/v1/download/{filename}`)
- Export output file list with download links
- "Cancel" button that calls `session_status` and surfaces it as abort

This turns vroidstudio-mcp from a fire-and-forget server into an observable pipeline with a control surface. Pairs with V5 (session JSONL) and cua-mcp F4 (evidence base64).

### V8 — VRoid Archetype Test Harness with Mock cua-mcp (1-2 days)
**Makes the test suite actually useful in CI.**

Current `test_project_workflows.py` presumably mocks some things but the depth is unknown. Build a proper mock HTTP server that stubs the cua-mcp HTTP endpoints (`/api/v1/control/tool`) and returns canned responses for:
- `automation_windows(find)` → `{"success": true, "result": {"data": {"handle": 12345}}}`
- `automation_keyboard(hotkey)` → `{"success": true}`
- `automation_assert(wait_stable)` → `{"success": true, "stable": true}`
- `automation_dialog(submit_path)` → `{"success": true}`

With this harness, every archetype can be run in CI without VRoid Studio. The full 55 archetypes can be smoke-tested in under a minute. Pairs with V4 (dry run mode).

---

## Priority Matrix

| # | Item | Sev | Effort |
|---|------|-----|--------|
| Bug 1 | cua-mcp tools may not be registered | Critical | → cua-mcp Bug 2 first |
| Bug 2 | preflight doesn't check cua-mcp tools | Critical | 1h |
| Bug 3 | Sample coord no calibration check | Critical | 1h |
| Bug 4 | webapp/web_sota ambiguity + dist in git | High | 1h |
| Bug 5 | sysadmin_client duplication | High | 30 min |
| Bug 6 | Smoke tests not in CI | High | 2h |
| Bug 7 | No CHANGELOG | Medium | 30 min |
| Bug 8-12 | Config dup, test state, operation strings | Medium | 2h |
| Bug 13-16 | Housekeeping | Low | 1h |
| V1 | Migrate to automation_task | High | 2-3 days |
| V2 | VRoid template library | High | 0.5 day |
| V3 | Health check operation | High | 0.5 day |
| V4 | Dry run mode | Medium | 1 day |
| V5 | Session replay from JSONL | Medium | 1 day |
| V6 | Archetype parameterisation | Medium | 1 day |
| V7 | Webapp live session monitor | Low | 1 day |
| V8 | Mock cua-mcp test harness | Low | 1-2 days |

**Recommended Cursor session order (post-reconciliation):**
1. Commit + push local reliability fixes (parser, path auto-detect, smoke scripts)
2. Critical 2 + 3 — cua tool preflight + sample-click calibration warn
3. V3 — `health_check` operation
4. V2 — real template captures at 2.3.0 / your DPI (pairs with cua-mcp F1)
5. V7 — wire vroidstudio session status into cua-mcp Targets page (W1)

---

## VRoid as CUA Test Subject

VRoid Studio is a genuinely hard CUA target and worth treating as the primary regression benchmark for cua-mcp:

- **Unity/GPU rendering** means screenshots are non-deterministic frame-to-frame even with no user input. This tests `wait_stable` and region masking harder than any office app.
- **No UIA tree** for most controls means template matching and OCR are mandatory, not optional. Every cua-mcp vision feature gets exercised.
- **Foreground-only input** for a GPU app tests the dispatch policy separation between VRoid (always foreground) and LibreOffice (can use background UIA).
- **Long operations** (model loading 3-8s, export 5-15s) test timeout tuning, progress reporting, and the evidence trail on timeout failures.
- **Modal dialogs** with locale-sensitive text test `automation_dialog` and `assert_text` with Tesseract.
- **55 distinct workflows** of varying complexity make it easy to find regression points — if `female_anime_sample_minimal` breaks but `male_blank` works, the bug is in sample picker handling.

Any CUA feature that works on VRoid will work on anything easier.
