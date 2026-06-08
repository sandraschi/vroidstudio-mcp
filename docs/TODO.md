# vroidstudio-mcp — TODO

Canonical backlog: [ASSESSMENT_2026-06-08.md](ASSESSMENT_2026-06-08.md) (reconciled 2026-06-08).

Operator console spec (fleet): [TARGETS_PAGE_SKETCH.md](../../pywinauto-mcp/docs/TARGETS_PAGE_SKETCH.md).

## Next (priority)

| # | Item | Status |
|---|------|--------|
| 1 | Push local fixes: VRoid path auto-detect, `structured_content` parser, HWND `windows[]` | ready |
| 2 | Preflight: verify cua-mcp tool list (`automation_assert`, `automation_task`, …) | open |
| 3 | Sample-click calibration / template assert before `quick_gal` | open — **blocks live export** |
| 4 | `vroid_studio(operation="health_check")` | open |
| 5 | Smoke scripts in CI with `requires_vroid` marker | open |
| 6 | `CHANGELOG.md` | open |

## Done (session)

- `automation_task` wiring + resume (v0.3.4–0.3.5)
- system-admin preflight crossconnect
- Smoke scripts: `scripts/smoke_e2e.py`, `smoke_start.ps1`, `run_smoke_export.py`
