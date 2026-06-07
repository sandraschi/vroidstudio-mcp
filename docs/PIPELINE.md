# Pipeline integration

vroidstudio-mcp is the **VRoid Studio GUI export** leg of the fleet avatar pipeline.

## Upstream / downstream

```text
pywinauto-mcp (10789)
    → vroidstudio-mcp (10881)  quick_gal_export
        → avatar-mcp (10793)     avatar_pipeline
            → blender-mcp (10849)
                → VTube / registry
```

## When to use this vs Hub

| Source | Use |
|--------|-----|
| VRoid Hub published model | avatar-mcp `hub_download` |
| Custom edit in VRoid Studio | vroidstudio-mcp `quick_gal_export` |
| Booth / creature VRM | avatar-mcp `hub_stage_file` (skip vroidstudio) |

## Calibrate sample model pick

Set on the host running vroidstudio-mcp:

```powershell
$env:VROID_SAMPLE_MODEL_X = "640"
$env:VROID_SAMPLE_MODEL_Y = "420"
```

Use `screenshot` operation to verify UI layout after VRoid updates.

## Central documentation

- `mcp-central-docs/integrations/vroidstudio/README.md`
- `mcp-central-docs/docs/avatars/FLEET_VRM_PIPELINE.md`
