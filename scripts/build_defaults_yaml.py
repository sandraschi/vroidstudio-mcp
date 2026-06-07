"""Build config/defaults.yaml from step_builder (shortcut-first templates)."""

from __future__ import annotations

from pathlib import Path

import yaml

from vroidstudio_mcp.step_builder import build_templates


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 2,
        "description": "VRoid Studio step templates — generated from step_builder.py (shortcut-first)",
        "calibration": {
            "resolution": [1920, 1080],
            "notes": "Clicks only for sample tile and preset thumbnails. All navigation via shortcuts.",
        },
        "templates": build_templates(),
    }

    text = yaml.dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False)
    path = config_dir / "defaults.yaml"
    path.write_text(text, encoding="utf-8")

    bundled = root / "src" / "vroidstudio_mcp" / "config" / "defaults.yaml"
    bundled.parent.mkdir(parents=True, exist_ok=True)
    bundled.write_text(text, encoding="utf-8")
    print(f"Wrote {len(payload['templates'])} templates to {path}")


if __name__ == "__main__":
    main()
