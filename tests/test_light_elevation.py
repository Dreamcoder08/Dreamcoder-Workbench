"""Light & elevation tier: one key light, warm-ink shadows, radius and border scale.

Spec: odd/tasks/dreamcoder-light-coherence.md, T4 (S2, S3, S6); design in L9.
"""

from __future__ import annotations

import copy
import json
import re
from itertools import pairwise
from pathlib import Path

import jsonschema
import pytest

from dreamcoder_theme.color_space import hex_to_oklch
from dreamcoder_theme.elevation import palette_keys, resolve_components
from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_hypr_waybar_rofi import (
    hypr_colors_conf_content,
    rofi_content,
    rofi_matugen_content,
    waybar_content,
)
from dreamcoder_theme.token_tiers import TierError

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
SCHEMA = ROOT / "DreamcoderThemes/dreamcoder/tokens.schema.json"
LEVELS = ("e1", "e2", "e3", "e4")
LAYER = re.compile(
    r"^0 (\d+(?:\.\d+)?)(?:px)? (\d+(?:\.\d+)?)px rgba\((\d+), (\d+), (\d+), (0\.\d+)\)$"
)


def _tokens() -> dict:
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def _layers(shadow: str) -> list[re.Match[str]]:
    parts = re.split(r",\s*(?=0 )", shadow)
    matches = [LAYER.match(part.strip()) for part in parts]
    assert all(matches), shadow
    return [m for m in matches if m]


def _parse(level: str) -> tuple[float, float, float, float]:
    """(key blur, key y, ambient blur, key alpha) of one shadow string."""
    key, ambient = _layers(resolve_components(_tokens(), "light")["elevation"][level])
    return float(key[2]), float(key[1]), float(ambient[2]), float(key[6])


def test_components_validate_against_the_schema() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(_tokens(), schema)


def _mutate(path: list[str | int], value: object) -> dict:
    tokens = copy.deepcopy(_tokens())
    node = tokens["components"]
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = value
    return tokens


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (["elevation", "levels", "e1", "z"], -1),
        (["elevation", "levels", "e1", "z"], "1"),
        (["elevation", "levels", "e2", "key_alpha"], 1.5),
        (["elevation", "levels", "e3", "ambient_alpha"], -0.1),
        (["elevation", "ink", "light"], "#1e1813"),
        (["radius", "r2"], "8px"),
        (["radius", "r3"], -4),
        (["border", "hairline", "width"], 0),
        (["border", "hairline", "color", "light"], "ink620"),
    ],
)
def test_schema_rejects_malformed_components(path: list[str | int], value: object) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(_mutate(path, value), schema)


def test_schema_rejects_a_missing_elevation_level() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    tokens = copy.deepcopy(_tokens())
    del tokens["components"]["elevation"]["levels"]["e4"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(tokens, schema)


def test_every_level_is_a_key_plus_ambient_layer_falling_straight_down() -> None:
    resolved = resolve_components(_tokens(), "light")
    assert tuple(resolved["elevation"]) == LEVELS
    for level in LEVELS:
        key, ambient = _layers(resolved["elevation"][level])
        z = float(key[2])
        assert float(key[1]) == z / 2  # key: 0 {0.5z}px {z}px
        assert float(ambient[1]) == 0.0  # ambient: 0 0 {2z}px
        assert float(ambient[2]) == 2 * z


def test_depth_grows_geometrically() -> None:
    zs = [_parse(level)[0] for level in LEVELS]
    assert zs[0] == 1
    assert zs == sorted(zs)
    ratios = [b / a for a, b in pairwise(zs)]
    assert all(2.0 <= r <= 3.2 for r in ratios), ratios


def test_alphas_increase_with_elevation() -> None:
    key_alphas = [_parse(level)[3] for level in LEVELS]
    ambient_alphas = []
    for level in LEVELS:
        ambient = _layers(resolve_components(_tokens(), "light")["elevation"][level])[1]
        ambient_alphas.append(float(ambient[6]))
    assert key_alphas == sorted(set(key_alphas))
    assert ambient_alphas == sorted(set(ambient_alphas))
    assert all(a < k for a, k in zip(ambient_alphas, key_alphas, strict=True))


def test_shadow_colour_is_warm_ink_never_black() -> None:
    resolved = resolve_components(_tokens(), "light")
    ink = resolved["shadow_ink"]
    assert ink == "#1e1813"  # ink.215, the Light text colour
    _, chroma, hue = hex_to_oklch(ink)
    assert chroma > 0.005
    assert 40 <= hue <= 85
    for level in LEVELS:
        for layer in _layers(resolved["elevation"][level]):
            rgb = tuple(int(layer[i]) for i in (3, 4, 5))
            assert rgb != (0, 0, 0)
            assert rgb == (0x1E, 0x18, 0x13)


def test_radius_and_border_scale() -> None:
    resolved = resolve_components(_tokens(), "light")
    assert resolved["radius"] == {"r1": "4px", "r2": "8px", "r3": "12px"}
    assert resolved["border"]["hairline"] == "1px"


def test_unknown_primitive_is_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["elevation"]["ink"]["light"] = "ink.999"
    with pytest.raises(TierError, match=r"ink\.999"):
        resolve_components(tokens, "light")
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["border"]["hairline"]["color"]["light"] = "paper.missing"
    with pytest.raises(TierError, match=r"paper\.missing"):
        resolve_components(tokens, "light")


def test_non_increasing_depth_is_a_tier_error() -> None:
    tokens = copy.deepcopy(_tokens())
    tokens["components"]["elevation"]["levels"]["e2"]["z"] = 1
    with pytest.raises(TierError, match="e2"):
        resolve_components(tokens, "light")


def test_modes_without_a_component_colour_resolve_to_nothing() -> None:
    assert resolve_components(_tokens(), "dark") == {}
    assert palette_keys(_tokens(), "dark") == {}


def test_palette_keys_flatten_for_the_renderers() -> None:
    keys = palette_keys(_tokens(), "light")
    assert keys["shadow_ink"] == "#1e1813"
    assert keys["radius_r3"] == "12px"
    assert keys["border_hairline"] == "1px"
    assert keys["elevation_e3"] == resolve_components(_tokens(), "light")["elevation"]["e3"]
    assert all(isinstance(v, str) for v in keys.values())


def test_load_variants_adds_elevation_to_light_only() -> None:
    merged = load_variants(VARIANTS, TOKENS)
    assert merged["light"]["shadow_ink"] == "#1e1813"
    assert not [k for k in merged["dark"] if k.startswith(("elevation_", "radius_", "shadow_"))]
    assert not [k for k in merged["dusk"] if k.startswith(("elevation_", "radius_", "shadow_"))]


def _light() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS)["light"]


def _dark() -> dict[str, str]:
    return load_variants(VARIANTS, TOKENS)["dark"]


def test_light_waybar_modules_use_the_e1_shadow_and_r2_radius() -> None:
    css = waybar_content(_light())
    assert f"box-shadow: {_light()['elevation_e1']};" in css
    assert f"border-radius: {_light()['radius_r2']};" in css


def test_light_rofi_uses_the_radius_scale() -> None:
    css = rofi_content(_light())
    assert "border-radius: 12px;" in css
    assert "border-radius: 8px;" in css
    assert "18px" not in css


def test_light_shadow_and_scrim_are_warm_ink_not_black() -> None:
    assert "shadow: #1e1813;" in rofi_matugen_content(_light())
    conf = hypr_colors_conf_content(_light())
    assert "$shadow = rgba(1e1813ff)" in conf
    assert "000000" not in conf


def test_dark_renderers_keep_their_legacy_literals() -> None:
    dark = _dark()
    assert "box-shadow" not in waybar_content(dark)
    assert "border-radius: 18px;" in rofi_content(dark)
    assert "shadow: #000000;" in rofi_matugen_content(dark)
    assert "$shadow = rgba(000000ff)" in hypr_colors_conf_content(dark)
