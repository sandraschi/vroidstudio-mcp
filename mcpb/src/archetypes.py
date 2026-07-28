"""Load and validate archetype definitions from YAML."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

EXPECTED_ARCHETYPE_COUNT = 55


@dataclass
class StepDef:
    action: str
    name: str = ""
    keys: list[str] = field(default_factory=list)
    key: str = ""
    text: str = ""
    x: int | None = None
    y: int | None = None
    seconds: float | None = None
    path: str = ""
    state: str = ""
    shortcut: str = ""
    require_change: bool = True
    optional: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> StepDef:
        return cls(
            action=str(raw.get("action", "")),
            name=str(raw.get("name", raw.get("action", "step"))),
            keys=list(raw.get("keys") or []),
            key=str(raw.get("key", "")),
            text=str(raw.get("text", "")),
            x=raw.get("x"),
            y=raw.get("y"),
            seconds=raw.get("seconds"),
            path=str(raw.get("path", "")),
            state=str(raw.get("state", "")),
            shortcut=str(raw.get("shortcut", "")),
            require_change=bool(raw.get("require_change", True)),
            optional=bool(raw.get("optional", False)),
        )


@dataclass
class ArchetypeDef:
    id: str
    display_name: str
    category: str
    template: str
    tags: list[str] = field(default_factory=list)
    export_name: str = ""
    sample_click: dict[str, int] | None = None
    extra_steps: list[StepDef] = field(default_factory=list)
    skip_sample: bool = False

    @classmethod
    def from_dict(cls, archetype_id: str, raw: dict[str, Any]) -> ArchetypeDef:
        extra = [StepDef.from_dict(s) for s in raw.get("extra_steps") or []]
        sample = raw.get("sample_click")
        return cls(
            id=archetype_id,
            display_name=str(raw.get("display_name", archetype_id)),
            category=str(raw.get("category", "general")),
            template=str(raw.get("template", "female_sample_minimal")),
            tags=list(raw.get("tags") or []),
            export_name=str(raw.get("export_name", f"{archetype_id}.vrm")),
            sample_click=dict(sample) if isinstance(sample, dict) else None,
            extra_steps=extra,
            skip_sample=bool(raw.get("skip_sample", False)),
        )


@dataclass
class ArchetypeCatalog:
    version: int
    templates: dict[str, list[StepDef]]
    calibration: dict[str, Any]
    archetypes: dict[str, ArchetypeDef]

    def list_ids(self) -> list[str]:
        return sorted(self.archetypes.keys())

    def get(self, archetype_id: str) -> ArchetypeDef:
        if archetype_id not in self.archetypes:
            raise KeyError(f"Unknown archetype: {archetype_id}")
        return self.archetypes[archetype_id]

    def resolve_steps(self, archetype_id: str) -> list[StepDef]:
        arch = self.get(archetype_id)
        template_steps = list(self.templates.get(arch.template, []))
        steps: list[StepDef] = []
        for step in template_steps:
            if step.action == "sample_click" and arch.skip_sample:
                continue
            steps.append(step)
        if arch.sample_click and not arch.skip_sample:
            for i, step in enumerate(steps):
                if step.action == "sample_click":
                    steps[i] = StepDef(
                        action="click",
                        name=step.name or "pick_sample",
                        x=arch.sample_click.get("x"),
                        y=arch.sample_click.get("y"),
                        state=step.state or "sample_selected",
                        require_change=step.require_change,
                    )
                    break
        steps.extend(arch.extra_steps)
        export_step = StepDef(action="set_export_name", name="export_name", text=arch.export_name)
        steps.append(export_step)
        return steps


def _parse_steps(raw_steps: list[dict[str, Any]] | None) -> list[StepDef]:
    return [StepDef.from_dict(s) for s in raw_steps or []]


def load_catalog(archetypes_path: Path, defaults_path: Path) -> ArchetypeCatalog:
    if not defaults_path.is_file():
        raise FileNotFoundError(f"Missing defaults config: {defaults_path}")
    if not archetypes_path.is_file():
        raise FileNotFoundError(f"Missing archetypes config: {archetypes_path}")

    defaults = yaml.safe_load(defaults_path.read_text(encoding="utf-8")) or {}
    archetypes_raw = yaml.safe_load(archetypes_path.read_text(encoding="utf-8")) or {}

    templates: dict[str, list[StepDef]] = {}
    for name, body in (defaults.get("templates") or {}).items():
        templates[name] = _parse_steps(body.get("steps"))

    calibration = defaults.get("calibration") or {}
    version = int(archetypes_raw.get("version", defaults.get("version", 1)))

    archetypes: dict[str, ArchetypeDef] = {}
    for arch_id, body in (archetypes_raw.get("archetypes") or {}).items():
        archetypes[arch_id] = ArchetypeDef.from_dict(arch_id, body or {})

    catalog = ArchetypeCatalog(
        version=version,
        templates=templates,
        calibration=calibration,
        archetypes=archetypes,
    )

    count = len(catalog.archetypes)
    if count != EXPECTED_ARCHETYPE_COUNT:
        raise ValueError(f"Expected {EXPECTED_ARCHETYPE_COUNT} archetypes, found {count}")

    logger.info("Loaded %d archetypes from %s", count, archetypes_path)
    return catalog
