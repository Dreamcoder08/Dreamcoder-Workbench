"""Light rhythm tier: 4 px spacing grid, motion physics and the shared type system.

Spec: odd/tasks/dreamcoder-light-coherence.md, T5 (S2, S3); design in L20.

Spacing is a 4 px grid (a single base unit keeps every gap a multiple of the one
below it). Motion durations step by ~1.6x (perceptual just-noticeable difference)
and curves approximate a critically damped spring: no overshoot, so every bezier
y control point stays within [0, 1]. Light and Dark share one type system.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import jsonschema
import pytest

from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_hypr_waybar_rofi import (
    hypr_content,
    rofi_content,
    waybar_content,
)
from dreamcoder_theme.rhythm import palette_keys, resolve_rhythm
from dreamcoder_theme.token_tiers import TierError

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / "DreamcoderThemes/dreamcoder"
TOKENS = THEMES / "tokens.json"
SCHEMA = THEMES / "tokens.schema.json"
GRID = 4
DURATIONS = ("quick", "base", "slow")
CURVES = ("enter", "exit", "move")
# padding / margin / gap / spacing / radius declarations carrying px lengths
DECLARATION = re.compile(
    r"(?:^|[\s{;])(padding|margin|spacing|border-radius|radius)\s*:\s*([^;]+);", re.MULTILINE
)
HYPR_GAP = re.compile(r"^\s*(gaps_in|gaps_out)\s*=\s*(.+?)\s*$", re.MULTILINE)
HYPR_BEZIER = re.compile(r"^\s*bezier\s*=\s*(\w+),\s*([^\n]+)$", re.MULTILINE)
HYPR_ANIMATION = re.compile(r"^\s*animation\s*=\s*([^\n]+)$", re.MULTILINE)


def _tokens() -> dict:
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def _schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _light() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS)["light"]


def _dark() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS)["dark"]


def _px_values(css: str) -> list[tuple[str, float]]:
    found: list[tuple[str, float]] = []
    for prop, value in DECLARATION.findall(css):
        found.extend((prop, float(n)) for n in re.findall(r"(-?\d+(?:\.\d+)?)px", value))
    return found


def _mutate(section: str, path: list[str | int], value: object) -> dict:
    tokens = copy.deepcopy(_tokens())
    node = tokens["components"][section]
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = value
    return tokens


# --- tokens and schema -------------------------------------------------------


def test_rhythm_tokens_exist_and_validate_against_the_schema() -> None:
    tokens = _tokens()
    assert {"spacing", "motion", "typography"} <= set(tokens["components"])
    assert "typography" in tokens["modes"]["light"]
    jsonschema.validate(tokens, _schema())


def test_light_shares_the_dark_type_system() -> None:
    modes = _tokens()["modes"]
    assert modes["light"]["typography"] == modes["dark"]["typography"]
    assert modes["light"]["typography"] == {
        "body_weight": 400,
        "emphasis_weight": 500,
        "heading_weight": 600,
        "letter_spacing": "0em",
        "uppercase_letter_spacing": "0.04em",
    }


@pytest.mark.parametrize(
    ("section", "path", "value"),
    [
        ("spacing", ["s2"], 6),
        ("spacing", ["s3"], "12px"),
        ("spacing", ["s1"], 0),
        ("spacing", ["s9"], 36),
        ("motion", ["duration", "quick"], -120),
        ("motion", ["duration", "base"], "200ms"),
        ("motion", ["duration", "slow"], 0),
        ("motion", ["curve", "enter"], [0.22, 1.2, 0.36, 1]),
        ("motion", ["curve", "exit"], [0.4, -0.1, 1, 1]),
        ("motion", ["curve", "move"], [1.2, 0, 0.2, 1]),
        ("motion", ["curve", "move"], [0.33, 0, 0.2]),
        ("motion", ["curve", "bounce"], [0.3, 0, 0.2, 1]),
        ("typography", ["font_family", "mono"], ""),
        ("typography", ["font_family", "mono"], 12),
    ],
)
def test_schema_rejects_malformed_rhythm_components(
    section: str, path: list[str | int], value: object
) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(_mutate(section, path, value), _schema())


@pytest.mark.parametrize("section", ["spacing", "motion", "typography"])
def test_schema_requires_every_rhythm_section(section: str) -> None:
    tokens = copy.deepcopy(_tokens())
    del tokens["components"][section]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, _schema())


@pytest.mark.parametrize(
    ("key", "value"),
    [("body_weight", 50), ("heading_weight", "600"), ("letter_spacing", 0)],
)
def test_schema_rejects_a_malformed_light_typography(key: str, value: object) -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["modes"]["light"]["typography"][key] = value
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, _schema())


def test_schema_requires_light_typography() -> None:
    tokens = copy.deepcopy(_tokens())
    del tokens["modes"]["light"]["typography"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, _schema())


# --- resolver ----------------------------------------------------------------


def test_resolver_exposes_spacing_motion_and_typography() -> None:
    resolved = resolve_rhythm(_tokens(), "light")
    assert resolved["spacing"] == {
        "s1": "4px",
        "s2": "8px",
        "s3": "12px",
        "s4": "16px",
        "s6": "24px",
        "s8": "32px",
    }
    assert resolved["motion"]["duration"] == {"quick": "120ms", "base": "200ms", "slow": "320ms"}
    assert resolved["motion"]["curve"] == {
        "enter": "cubic-bezier(0.22, 1, 0.36, 1)",
        "exit": "cubic-bezier(0.4, 0, 1, 1)",
        "move": "cubic-bezier(0.33, 0, 0.2, 1)",
    }
    assert resolved["typography"]["body_weight"] == 400
    assert resolved["typography"]["font_family"]["mono"]


def test_spacing_sits_on_the_four_pixel_grid() -> None:
    spacing = _tokens()["components"]["spacing"]
    assert spacing["s1"] == GRID
    assert all(v % GRID == 0 for v in spacing.values())
    assert list(spacing.values()) == sorted(spacing.values())


def test_durations_are_monotone() -> None:
    durations = [_tokens()["components"]["motion"]["duration"][k] for k in DURATIONS]
    assert durations == sorted(set(durations))


def test_curves_never_overshoot() -> None:
    for name in CURVES:
        x1, y1, x2, y2 = _tokens()["components"]["motion"]["curve"][name]
        assert 0 <= x1 <= 1 and 0 <= x2 <= 1, name
        assert 0 <= y1 <= 1 and 0 <= y2 <= 1, name


def test_non_monotone_durations_are_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["motion"]["duration"]["base"] = 100
    with pytest.raises(TierError, match="base"):
        resolve_rhythm(tokens, "light")


def test_an_overshooting_curve_is_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["motion"]["curve"]["enter"] = [0.22, 1.3, 0.36, 1]
    with pytest.raises(TierError, match="enter"):
        resolve_rhythm(tokens, "light")


def test_an_off_grid_spacing_step_is_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["spacing"]["s2"] = 6
    with pytest.raises(TierError, match="s2"):
        resolve_rhythm(tokens, "light")


def test_modes_without_the_component_tier_resolve_to_nothing() -> None:
    assert resolve_rhythm(_tokens(), "dark") == {}
    assert palette_keys(_tokens(), "dark") == {}


def test_palette_keys_flatten_for_the_renderers() -> None:
    keys = palette_keys(_tokens(), "light")
    assert keys["space_s3"] == "12px"
    assert keys["motion_duration_quick"] == "120ms"
    assert keys["motion_curve_enter"] == "cubic-bezier(0.22, 1, 0.36, 1)"
    assert keys["type_emphasis_weight"] == "500"
    assert all(isinstance(v, str) for v in keys.values())


def test_load_variants_adds_rhythm_to_light_only() -> None:
    assert _light()["space_s1"] == "4px"
    assert _light()["motion_duration_slow"] == "320ms"
    prefixes = ("space_", "motion_", "type_", "font_")
    assert not [k for k in _dark() if k.startswith(prefixes)]


# --- renderers: the 4 px grid ------------------------------------------------


def _light_artifacts() -> dict[str, str]:
    return {
        "waybar": waybar_content(_light()),
        "rofi": rofi_content(_light()),
        "waybar-light.css": (THEMES / "waybar-light.css").read_text(encoding="utf-8"),
        "rofi-light.rasi": (THEMES / "rofi-light.rasi").read_text(encoding="utf-8"),
    }


@pytest.mark.parametrize("name", ["waybar", "rofi", "waybar-light.css", "rofi-light.rasi"])
def test_every_light_padding_margin_gap_and_radius_is_on_the_grid(name: str) -> None:
    values = _px_values(_light_artifacts()[name])
    assert values, f"{name}: no spacing declarations found"
    off = [(prop, v) for prop, v in values if v % GRID]
    assert not off, f"{name}: off the {GRID}px grid: {off}"


def test_light_waybar_and_rofi_carry_spacing_declarations() -> None:
    kinds = {prop for prop, _ in _px_values(waybar_content(_light()))}
    assert {"padding", "margin", "border-radius"} <= kinds
    kinds = {prop for prop, _ in _px_values(rofi_content(_light()))}
    assert {"padding", "border-radius"} <= kinds


def test_light_hyprland_gaps_are_on_the_grid() -> None:
    for content in (hypr_content(_light()), (THEMES / "hyprland-light.conf").read_text("utf-8")):
        gaps = dict(HYPR_GAP.findall(content))
        assert set(gaps) == {"gaps_in", "gaps_out"}
        assert all(int(v) % GRID == 0 for v in gaps.values()), gaps
        assert int(gaps["gaps_in"]) < int(gaps["gaps_out"])


# --- renderers: motion -------------------------------------------------------


def test_light_hyprland_curves_never_overshoot() -> None:
    content = hypr_content(_light())
    curves = HYPR_BEZIER.findall(content)
    assert {name for name, _ in curves} == {"dc_enter", "dc_exit", "dc_move"}
    for name, raw in curves:
        x1, y1, x2, y2 = (float(n) for n in raw.split(","))
        assert 0 <= x1 <= 1 and 0 <= x2 <= 1, name
        assert 0 <= y1 <= 1 and 0 <= y2 <= 1, name


def test_light_hyprland_animations_use_the_token_durations_and_curves() -> None:
    content = hypr_content(_light())
    speeds_ds = {"quick": 1.2, "base": 2.0, "slow": 3.2}  # 1 ds = 100 ms
    entries = [[p.strip() for p in line.split(",")] for line in HYPR_ANIMATION.findall(content)]
    assert entries
    used = set()
    for _name, enabled, speed, curve, *_ in entries:
        assert enabled == "1"
        assert float(speed) in speeds_ds.values()
        assert curve in {"dc_enter", "dc_exit", "dc_move"}
        used.add(float(speed))
    assert used <= set(speeds_ds.values())
    assert speeds_ds["quick"] < speeds_ds["base"] < speeds_ds["slow"]


def test_light_hyprland_conf_matches_the_renderer() -> None:
    assert (THEMES / "hyprland-light.conf").read_text(encoding="utf-8") == hypr_content(_light())


# --- Dark stays untouched ----------------------------------------------------


def test_dark_artifacts_carry_no_rhythm() -> None:
    dark_hypr = hypr_content(_dark())
    assert "gaps_" not in dark_hypr
    assert "bezier" not in dark_hypr
    assert "animation" not in dark_hypr
    assert "padding" not in waybar_content(_dark())
    assert "margin" not in waybar_content(_dark())
    assert "padding" not in rofi_content(_dark())
    assert "font-weight" not in waybar_content(_dark())


@pytest.mark.parametrize(
    ("name", "render"),
    [
        ("hyprland-dark.conf", hypr_content),
        ("waybar-dark.css", waybar_content),
        ("rofi-dark.rasi", rofi_content),
    ],
)
def test_dark_files_match_their_renderers(name: str, render) -> None:
    assert (THEMES / name).read_text(encoding="utf-8") == render(_dark())
