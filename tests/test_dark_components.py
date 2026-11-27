"""Dark components: tonal elevation, shared geometry, token-derived effects, no literals.

Spec: odd/tasks/dreamcoder-dark-coherence.md, T3 (S1, S2, S5); design in L6.

On OLED black a drop shadow is invisible, so elevation is luminance: each level
resolves to a lighter graphite surface. Dark adopts the same mode-independent
geometry (radius, spacing, motion, type) as Light, and its glows come from the
semantic tokens they decorate instead of hand-copied hex.
"""

from __future__ import annotations

import json
import re
from itertools import pairwise
from pathlib import Path

import jsonschema
import pytest

from dreamcoder_theme._math import compute_on_color, mix
from dreamcoder_theme.color_space import hex_to_oklch, oklch_to_hex, parse_oklch
from dreamcoder_theme.effects import drift as effects_drift
from dreamcoder_theme.effects import resolve_effects
from dreamcoder_theme.elevation import adopts_components, resolve_components
from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_hypr_waybar_rofi import (
    hypr_colors_conf_content,
    hypr_content,
    rofi_content,
    rofi_matugen_content,
    waybar_content,
)
from dreamcoder_theme.renderers_opencode import opencode_content
from dreamcoder_theme.rhythm import palette_keys as rhythm_keys
from dreamcoder_theme.rhythm import resolve_rhythm

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / "DreamcoderThemes/dreamcoder"
TOKENS_FILE = THEMES / "tokens.json"
SCHEMA_FILE = THEMES / "tokens.schema.json"
LEVELS = ("e1", "e2", "e3", "e4")
GEOMETRY_PREFIXES = ("radius_", "space_", "motion_", "type_", "font_")


def _tokens() -> dict:
    return json.loads(TOKENS_FILE.read_text(encoding="utf-8"))


def _dark() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS_FILE)["dark"]


def _light() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS_FILE)["light"]


def _lightness(hex_color: str) -> float:
    return hex_to_oklch(hex_color)[0]


def _hex(name: str) -> str:
    return oklch_to_hex(*parse_oklch(_tokens()["primitives"]["dark"][name]))


def _rgb(hex_color: str) -> tuple[int, int, int]:
    return tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def _rgba_parts(css: str) -> tuple[tuple[int, int, int], float]:
    match = re.fullmatch(r"rgba\((\d+), (\d+), (\d+), (0?\.\d+)\)", css)
    assert match, css
    return (int(match[1]), int(match[2]), int(match[3])), float(match[4])


def _strip_ink(shadow: str) -> str:
    """A shadow with its colour removed: offsets, blurs and alphas only."""
    return re.sub(r"rgba\(\d+, \d+, \d+, ", "rgba(_, ", shadow)


def _geometry(palette: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in palette.items() if k.startswith(GEOMETRY_PREFIXES)}


# --- the component tier resolves for Dark ------------------------------------


def test_the_schema_accepts_the_dark_components() -> None:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    jsonschema.validate(_tokens(), schema)


def test_dark_adopts_the_component_tier() -> None:
    assert adopts_components(_tokens(), "dark")
    assert adopts_components(_tokens(), "light")


def test_shadow_ink_is_graphite_000_resolved_from_the_primitives() -> None:
    tokens = _tokens()
    assert tokens["components"]["elevation"]["ink"]["dark"] == "graphite.000"
    assert resolve_components(tokens, "dark")["shadow_ink"] == _hex("graphite.000") == "#000000"


def test_tonal_surfaces_rise_strictly_in_lightness() -> None:
    surfaces = resolve_components(_tokens(), "dark")["surface"]
    assert tuple(surfaces) == LEVELS
    lightness = [_lightness(surfaces[level]) for level in LEVELS]
    assert all(b - a >= 0.04 for a, b in pairwise(lightness)), lightness
    assert _lightness(surfaces["e1"]) > _lightness(_dark()["surface0"])


def test_tonal_surfaces_are_the_neutral_ladder_steps() -> None:
    surfaces = resolve_components(_tokens(), "dark")["surface"]
    dark = _dark()
    assert surfaces == {
        "e1": dark["surface1"],
        "e2": dark["surface2"],
        "e3": dark["surface3"],
        "e4": dark["selection"],
    }
    assert all(hex_to_oklch(value)[1] < 0.002 for value in surfaces.values())


def test_the_two_highest_levels_get_a_top_edge_one_step_lighter() -> None:
    resolved = resolve_components(_tokens(), "dark")
    assert tuple(resolved["edge"]) == ("e3", "e4")
    for level, edge in resolved["edge"].items():
        step = _lightness(edge) - _lightness(resolved["surface"][level])
        assert 0.03 <= step <= 0.06, (level, step)
        assert hex_to_oklch(edge)[1] < 0.002


def test_light_has_no_tonal_surfaces_or_edges() -> None:
    resolved = resolve_components(_tokens(), "light")
    assert "surface" not in resolved
    assert "edge" not in resolved
    assert not [k for k in _light() if k.startswith(("elevation_surface_", "elevation_edge_"))]


def test_palette_exposes_the_tonal_levels_to_renderers() -> None:
    dark = _dark()
    surfaces = resolve_components(_tokens(), "dark")["surface"]
    for level in LEVELS:
        assert dark[f"elevation_surface_{level}"] == surfaces[level]
    assert dark["elevation_edge_e3"] == resolve_components(_tokens(), "dark")["edge"]["e3"]
    assert dark["elevation_edge_e4"] == resolve_components(_tokens(), "dark")["edge"]["e4"]
    assert dark["shadow_ink"] == "#000000"


def test_dark_shadows_keep_lights_geometry_with_the_dark_ink() -> None:
    dark = resolve_components(_tokens(), "dark")["elevation"]
    light = resolve_components(_tokens(), "light")["elevation"]
    assert tuple(dark) == LEVELS
    for level in LEVELS:
        assert _strip_ink(dark[level]) == _strip_ink(light[level])
        assert "rgba(0, 0, 0, " in dark[level]


# --- one geometry for both modes --------------------------------------------


def test_dark_radius_equals_lights() -> None:
    dark = resolve_components(_tokens(), "dark")
    light = resolve_components(_tokens(), "light")
    assert dark["radius"] == light["radius"] == {"r1": "4px", "r2": "8px", "r3": "12px"}
    assert dark["border"]["hairline"] == light["border"]["hairline"]


def test_dark_rhythm_and_motion_equal_lights() -> None:
    dark = resolve_rhythm(_tokens(), "dark")
    light = resolve_rhythm(_tokens(), "light")
    assert dark
    assert dark == light


def test_every_geometry_palette_key_is_identical_across_modes() -> None:
    assert _geometry(_dark())
    assert _geometry(_dark()) == _geometry(_light())
    assert rhythm_keys(_tokens(), "dark") == rhythm_keys(_tokens(), "light")


# --- generated desktop chrome ------------------------------------------------


def _animations(css: str) -> str:
    match = re.search(r"animations \{.*?\n\}", css, re.S)
    assert match, css
    return match[0]


def test_dark_hyprland_gaps_and_animations_equal_lights() -> None:
    dark, light = hypr_content(_dark()), hypr_content(_light())
    for gap in ("gaps_in = 4", "gaps_out = 16"):
        assert gap in dark
    assert _animations(dark) == _animations(light)
    assert "bezier = dc_enter, 0.22, 1, 0.36, 1" in dark


def test_dark_hyprland_keeps_its_ink_gradient_border() -> None:
    dark = _dark()
    assert f"col.active_border = rgba({dark['text'][1:]}ff) rgba({dark['muted'][1:]}ff) 45deg" in (
        hypr_content(dark)
    )


def test_dark_waybar_modules_share_lights_rhythm_and_use_the_e1_shadow() -> None:
    css = waybar_content(_dark())
    dark = _dark()
    assert f"box-shadow: {dark['elevation_e1']};" in css
    for declaration in (
        "border-radius: 8px;",
        "padding: 0 12px;",
        "margin: 4px;",
        "font-weight: 400;",
        "padding: 0 8px;",
        "font-weight: 500;",
    ):
        assert declaration in css, declaration
    # Light-only semantic chrome stays Light-only.
    assert "custom-updates" not in css
    assert "@selection" not in css


def test_dark_rofi_shares_lights_radii_and_padding() -> None:
    css = rofi_content(_dark())
    assert "border-radius: 12px;" in css
    assert "border-radius: 8px;" in css
    assert "18px" not in css
    assert "padding: 8px 12px;" in css
    assert "listview { spacing: 4px; }" in css


def test_dark_rofi_window_takes_the_e3_top_edge() -> None:
    dark = _dark()
    css = rofi_content(dark)
    assert f"border-color: {dark['elevation_edge_e3']} {dark['border_ui']}" in css


def test_dark_shadow_and_scrim_come_from_the_elevation_ink() -> None:
    dark = _dark()
    ink = dark["shadow_ink"]
    assert f"shadow: {ink};" in rofi_matugen_content(dark)
    assert f"$shadow = rgba({ink[1:]}ff)" in hypr_colors_conf_content(dark)
    for role in ("scrim", "overlay"):
        assert _rgba_parts(dark[role])[0] == _rgb(ink), role


def test_opencode_dark_shadow_mixes_the_elevation_ink_into_the_canvas() -> None:
    dark = _dark()
    theme = json.loads(opencode_content(dark, transparent_background=True))["theme"]
    assert theme["shadow"] == mix(dark["bg"], dark["shadow_ink"], 0.25)


def test_opencode_without_components_keeps_its_fallback_ink() -> None:
    bare = {k: v for k, v in _dark().items() if k != "shadow_ink"}
    theme = json.loads(opencode_content(bare, transparent_background=True))["theme"]
    assert theme["shadow"] == mix(bare["bg"], "#000000", 0.25)


# --- Light stays byte-identical ---------------------------------------------


@pytest.mark.parametrize(
    ("name", "render"),
    [
        ("hyprland-light.conf", hypr_content),
        ("waybar-light.css", waybar_content),
        ("rofi-light.rasi", rofi_content),
        ("hypr-colors-light.conf", hypr_colors_conf_content),
    ],
)
def test_light_files_match_their_renderers(name: str, render) -> None:
    assert (THEMES / name).read_text(encoding="utf-8") == render(_light())


def test_light_keeps_its_gradientless_frame_and_chips() -> None:
    light = _light()
    assert f"col.active_border = rgba({light['accent'][1:]}ff)\n" in hypr_content(light)
    assert "custom-updates" in waybar_content(light)


# --- effects derive from tokens ---------------------------------------------

GLOWS = {
    # name: (source mode token, blur px, spread px, alpha) — unchanged geometry.
    "glow_brand": ("aliases.brand", 24, 0, 0.28),
    "glow_focus": ("focus", 0, 3, 0.30),
    "glow_error": ("error", 20, 0, 0.22),
}


def _source(name: str) -> str:
    node = _tokens()["modes"]["dark"]
    for step in name.split("."):
        node = node[step]
    return node


@pytest.mark.parametrize("glow", GLOWS)
def test_glow_colour_equals_its_source_token_with_unchanged_alpha_and_blur(glow: str) -> None:
    source, blur, spread, alpha = GLOWS[glow]
    stored = _tokens()["modes"]["dark"]["effects"][glow]
    match = re.fullmatch(r"0 0 (\d+)(?:px)? ?(\d+)?(?:px)? (rgba\(.*\))", stored)
    assert match, stored
    assert int(match[1]) == blur
    assert int(match[2] or 0) == spread
    rgb, got_alpha = _rgba_parts(match[3])
    assert rgb == _rgb(_source(source))
    assert got_alpha == alpha


def test_focus_glow_is_no_longer_the_legacy_blue() -> None:
    assert "59, 130, 246" not in _tokens()["modes"]["dark"]["effects"]["glow_focus"]


def test_stored_effects_equal_the_derived_effects() -> None:
    tokens = _tokens()
    assert resolve_effects(tokens, "dark") == tokens["modes"]["dark"]["effects"]
    assert effects_drift(tokens) == []


def test_light_has_no_effects() -> None:
    assert resolve_effects(_tokens(), "light") == {}


def test_effects_drift_names_a_stale_glow() -> None:
    tokens = _tokens()
    tokens["modes"]["dark"]["effects"]["glow_focus"] = "0 0 0 3px rgba(59, 130, 246, 0.30)"
    problems = effects_drift(tokens)
    assert len(problems) == 1
    assert problems[0].startswith("EFFECTS_DRIFT: dark.glow_focus")


# --- no legacy literals in the source ---------------------------------------


@pytest.mark.parametrize("literal", ["#100f0d", "#6FA0AF"])
def test_legacy_dark_literals_are_gone_from_src(literal: str) -> None:
    hits = [
        str(path.relative_to(ROOT))
        for path in (ROOT / "src").rglob("*")
        if path.suffix in {".py", ".json", ".md", ".sh"}
        and "__pycache__" not in path.parts
        and literal.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()
    ]
    assert hits == []


def test_on_color_fallback_is_the_oled_canvas_not_a_warm_black() -> None:
    assert compute_on_color("#ffffff", "dark") == "#000000"
    assert compute_on_color("#ffffff", "dark", dark_candidate="#ffffff") == "#000000"
    assert compute_on_color("#ffffff", "dark", canvas="#000000") == "#000000"


def test_herdr_ui_accent_is_the_dark_brand_token_not_a_literal() -> None:
    shipped = (ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder").rglob("*dark*")
    accents = [
        line
        for path in shipped
        if path.is_file()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("accent = ")
    ]
    assert accents
    assert set(accents) == {f'accent = "{_dark()["accent"]}"'}
