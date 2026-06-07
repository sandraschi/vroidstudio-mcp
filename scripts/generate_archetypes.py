"""Generate config/archetypes.yaml with exactly 55 archetypes."""

from __future__ import annotations

from pathlib import Path

import yaml

EXPECTED = 55

FEMALE_ANIME = [
    ("anime_gal_default", "Anime Gal Default", "female_sample_minimal", {"x": 960, "y": 420}),
    ("anime_gal_long_hair", "Anime Gal Long Hair", "female_sample_hair", {"x": 800, "y": 380}),
    ("anime_gal_short_hair", "Anime Gal Short Hair", "female_sample_hair", {"x": 1120, "y": 380}),
    ("anime_gal_twintail", "Anime Gal Twintails", "female_sample_hair", {"x": 640, "y": 380}),
    ("anime_gal_ponytail", "Anime Gal Ponytail", "female_sample_hair", {"x": 1280, "y": 380}),
    ("anime_gal_bob", "Anime Gal Bob Cut", "female_sample_hair", {"x": 720, "y": 460}),
    ("anime_gal_hime", "Anime Gal Hime Cut", "female_sample_hair", {"x": 880, "y": 460}),
    ("anime_gal_mature", "Anime Gal Mature", "female_sample_face", {"x": 1040, "y": 460}),
    ("anime_gal_idol", "Anime Gal Idol", "female_sample_outfit", {"x": 960, "y": 340}),
    ("anime_gal_gothic", "Anime Gal Gothic", "female_sample_outfit", {"x": 800, "y": 460}),
    ("anime_gal_sporty", "Anime Gal Sporty", "female_sample_outfit", {"x": 1120, "y": 460}),
    ("anime_gal_catgirl", "Anime Gal Catgirl", "female_sample_accessory", {"x": 640, "y": 340}),
    ("anime_gal_foxgirl", "Anime Gal Foxgirl", "female_sample_accessory", {"x": 1280, "y": 340}),
    ("anime_gal_glasses", "Anime Gal Glasses", "female_sample_face", {"x": 720, "y": 340}),
    ("anime_gal_magical", "Anime Gal Magical Girl", "female_sample_outfit", {"x": 880, "y": 340}),
]

MALE_ANIME = [
    ("anime_guy_default", "Anime Guy Default", "male_sample_minimal", {"x": 960, "y": 520}),
    ("anime_guy_long_hair", "Anime Guy Long Hair", "male_sample_hair", {"x": 800, "y": 520}),
    ("anime_guy_short_hair", "Anime Guy Short Hair", "male_sample_hair", {"x": 1120, "y": 520}),
    ("anime_guy_hero", "Anime Guy Hero", "male_sample_outfit", {"x": 640, "y": 520}),
    ("anime_guy_delinquent", "Anime Guy Delinquent", "male_sample_hair", {"x": 1280, "y": 520}),
    ("anime_guy_gentleman", "Anime Guy Gentleman", "male_sample_outfit", {"x": 720, "y": 600}),
    ("anime_guy_athlete", "Anime Guy Athlete", "male_sample_body", {"x": 880, "y": 600}),
    ("anime_guy_idol", "Anime Guy Idol", "male_sample_outfit", {"x": 1040, "y": 520}),
    ("anime_guy_gothic", "Anime Guy Gothic", "male_sample_outfit", {"x": 800, "y": 600}),
    ("anime_guy_nerd", "Anime Guy Nerd", "male_sample_face", {"x": 1120, "y": 600}),
    ("anime_guy_samurai", "Anime Guy Samurai", "male_sample_outfit", {"x": 640, "y": 600}),
    ("anime_guy_modern", "Anime Guy Modern Street", "male_sample_outfit", {"x": 1280, "y": 600}),
]

FEMALE_REALISTIC = [
    ("realistic_female_default", "Realistic Female Default", "female_sample_minimal", {"x": 960, "y": 420}),
    ("realistic_female_mature", "Realistic Female Mature", "female_sample_face", {"x": 1040, "y": 420}),
    ("realistic_female_young", "Realistic Female Young", "female_sample_face", {"x": 880, "y": 420}),
    ("realistic_female_athletic", "Realistic Female Athletic", "female_sample_body", {"x": 800, "y": 420}),
    ("realistic_female_professional", "Realistic Female Professional", "female_sample_outfit", {"x": 1120, "y": 420}),
]

MALE_REALISTIC = [
    ("realistic_male_default", "Realistic Male Default", "male_sample_minimal", {"x": 960, "y": 520}),
    ("realistic_male_mature", "Realistic Male Mature", "male_sample_face", {"x": 1040, "y": 520}),
    ("realistic_male_young", "Realistic Male Young", "male_sample_face", {"x": 880, "y": 520}),
    ("realistic_male_athletic", "Realistic Male Athletic", "male_sample_body", {"x": 800, "y": 520}),
    ("realistic_male_professional", "Realistic Male Professional", "male_sample_outfit", {"x": 1120, "y": 520}),
]

STYLIZED = [
    ("stylized_chibi_female", "Stylized Chibi Female", "female_sample_body", {"x": 960, "y": 380}),
    ("stylized_chibi_male", "Stylized Chibi Male", "male_sample_body", {"x": 960, "y": 560}),
    ("stylized_toon_female", "Stylized Toon Female", "female_sample_face", {"x": 720, "y": 420}),
    ("stylized_toon_male", "Stylized Toon Male", "male_sample_face", {"x": 720, "y": 520}),
    ("stylized_mascot", "Stylized Mascot", "female_sample_accessory", {"x": 1120, "y": 340}),
]

VTUBER = [
    ("vtuber_female", "VTuber Ready Female", "female_vtuber", {"x": 960, "y": 400}),
    ("vtuber_male", "VTuber Ready Male", "male_vtuber", {"x": 960, "y": 540}),
    ("vrchat_female", "VRChat Optimized Female", "female_editor_tour", {"x": 960, "y": 420}),
    ("vrchat_male", "VRChat Optimized Male", "male_editor_tour", {"x": 960, "y": 520}),
    ("stream_ready", "Stream Ready Neutral", "female_photo_booth", {"x": 1040, "y": 460}),
]

SEASONAL = [
    ("winter_female", "Winter Female", "female_sample_outfit", {"x": 800, "y": 400}),
    ("summer_female", "Summer Female", "female_sample_outfit", {"x": 1120, "y": 400}),
    ("winter_male", "Winter Male", "male_sample_outfit", {"x": 800, "y": 540}),
    ("summer_male", "Summer Male", "male_sample_outfit", {"x": 1120, "y": 540}),
    ("fantasy_elf", "Fantasy Elf", "female_sample_accessory", {"x": 1280, "y": 420}),
]

FLEET = [
    ("quick_gal", "Quick Gal (Fleet Legacy)", "female_sample_minimal", {"x": 960, "y": 420}),
    ("blank_female", "Blank Female", "female_blank", None),
    ("blank_male", "Blank Male", "male_blank", None),
]

CATEGORY_MAP = {
    "female_anime": FEMALE_ANIME,
    "male_anime": MALE_ANIME,
    "female_realistic": FEMALE_REALISTIC,
    "male_realistic": MALE_REALISTIC,
    "stylized": STYLIZED,
    "vtuber": VTUBER,
    "seasonal": SEASONAL,
    "fleet": FLEET,
}


def build_archetypes() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for category, entries in CATEGORY_MAP.items():
        for arch_id, display_name, template, click in entries:
            body: dict = {
                "display_name": display_name,
                "category": category,
                "template": template,
                "export_name": f"{arch_id}.vrm",
                "tags": [category.split("_")[0] if "_" in category else category],
            }
            if template.endswith("_blank"):
                body["skip_sample"] = True
            elif click:
                body["sample_click"] = click
            if arch_id == "quick_gal":
                body["tags"] = ["fleet", "legacy"]
            out[arch_id] = body
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    config_dir = root / "config"
    if not config_dir.is_dir():
        config_dir = root.parent / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    archetypes = build_archetypes()
    if len(archetypes) != EXPECTED:
        raise SystemExit(f"Generator produced {len(archetypes)} archetypes, expected {EXPECTED}")

    payload = {
        "version": 1,
        "description": "55 VRoid Studio puppet archetypes — config-driven, 1920x1080 baseline",
        "archetypes": archetypes,
    }
    path = config_dir / "archetypes.yaml"
    path.write_text(yaml.dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    bundled = root / "src" / "vroidstudio_mcp" / "config" / "archetypes.yaml"
    if bundled.parent.is_dir():
        bundled.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {len(archetypes)} archetypes to {path}")


if __name__ == "__main__":
    main()
