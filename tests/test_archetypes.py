"""Tests for archetype catalog loading."""

from pathlib import Path

import pytest

from vroidstudio_mcp.archetypes import EXPECTED_ARCHETYPE_COUNT, load_catalog


@pytest.fixture
def config_paths():
    root = Path(__file__).resolve().parents[1]
    bundled = root / "src" / "vroidstudio_mcp" / "config"
    repo = root / "config"
    if bundled.is_dir():
        return bundled / "archetypes.yaml", bundled / "defaults.yaml"
    return repo / "archetypes.yaml", repo / "defaults.yaml"


def test_loads_55_archetypes(config_paths):
    archetypes_path, defaults_path = config_paths
    catalog = load_catalog(archetypes_path, defaults_path)
    assert len(catalog.archetypes) == EXPECTED_ARCHETYPE_COUNT
    assert catalog.get("quick_gal").template == "female_sample_minimal"
    assert catalog.get("blank_male").skip_sample is True


def test_resolve_steps_includes_export(config_paths):
    archetypes_path, defaults_path = config_paths
    catalog = load_catalog(archetypes_path, defaults_path)
    steps = catalog.resolve_steps("anime_gal_twintail")
    names = [s.name or s.action for s in steps]
    assert "export_vrm" in names
    assert "export_dialog" in names
    assert any(s.action == "click" and s.name == "pick_sample" for s in steps)


def test_vtuber_archetypes_use_new_templates(config_paths):
    archetypes_path, defaults_path = config_paths
    catalog = load_catalog(archetypes_path, defaults_path)
    assert catalog.get("vtuber_female").template == "female_vtuber"
    assert catalog.get("vrchat_male").template == "male_editor_tour"
    assert catalog.get("stream_ready").template == "female_photo_booth"
def test_all_archetypes_have_templates(config_paths):
    archetypes_path, defaults_path = config_paths
    catalog = load_catalog(archetypes_path, defaults_path)
    for arch_id in catalog.list_ids():
        arch = catalog.get(arch_id)
        assert arch.template in catalog.templates, f"{arch_id} missing template {arch.template}"
