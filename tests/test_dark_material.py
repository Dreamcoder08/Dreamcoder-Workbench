"""Dreamcoder Dark material laws: graphite, emission and pigment at night density.

Spec: odd/tasks/dreamcoder-dark-coherence.md, T2 (S1-S5, design L4) and T9 (L12/L13: calm text).

The values live in tokens.json; these tests hold the physical model they must
obey, so a future edit cannot drift out of the system silently.
"""

from __future__ import annotations

import itertools
import json
import re
from pathlib import Path

import pytest

from dreamcoder_theme._math import apca_lc, contrast, hex_to_rgb
from dreamcoder_theme.color_space import delta_e2000, hex_to_oklch, parse_oklch
from dreamcoder_theme.token_tiers import drift, resolve_mode

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "DreamcoderThemes/dreamcoder/tokens.json").read_text(encoding="utf-8"))
DARK = TOKENS["modes"]["dark"]
PRIMS = TOKENS["primitives"].get("dark", {})
BIND = TOKENS["bindings"].get("dark", {})
RESOLVED = resolve_mode(TOKENS, "dark") if BIND else {}

SURFACES = ("bg", "bg_soft", "surface0", "surface1", "surface2", "surface3", "selection")
LADDER = ("surface0", "surface1", "surface2", "surface3", "selection")
TEXT_RAMP = ("text_heading", "text", "muted", "comment", "subtle", "disabled")
QUIET_SURFACES = ("bg", "bg_soft", "surface0", "surface1", "surface2", "selection")
# Hue order around the wheel, shared with Light: role -> pigment family.
PIGMENT_FAMILIES = {
    "error": "madder",
    "warning": "ochre",
    "success": "malachite",
    "focus": "verdigris",
    "info": "indigo",
    "accent": "iris",
    "lavender": "violet",
    "mauve": "cochineal",
}
PIGMENT_ROLES = tuple(PIGMENT_FAMILIES)
FAMILIES = ("graphite", *dict.fromkeys(PIGMENT_FAMILIES.values()))
HEX_ROLES = [
    k for k, v in DARK.items() if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v)
]


def _prim(role: str) -> tuple[float, float, float]:
    """OKLCH of what a role renders to (the shipped hex)."""
    return hex_to_oklch(DARK[role])


def _lightness(role: str) -> float:
    return _prim(role)[0]


def _rgba(role: str) -> tuple[tuple[int, int, int], float]:
    match = re.fullmatch(r"rgba\((\d+), (\d+), (\d+), ([0-9.]+)\)", DARK[role])
    assert match, DARK[role]
    return (int(match[1]), int(match[2]), int(match[3])), float(match[4])


def test_dark_primitives_exist_with_canonical_names() -> None:
    assert PRIMS, "primitives.dark is missing"
    assert {name.split(".")[0] for name in PRIMS} == set(FAMILIES)
    for name, value in PRIMS.items():
        family, per_mille = name.split(".")
        assert per_mille == f"{round(parse_oklch(value)[0] * 1000):03d}", name
        assert family in FAMILIES, name


def test_every_hex_role_is_bound_and_resolves_to_its_hex() -> None:
    assert HEX_ROLES
    assert set(HEX_ROLES) <= set(BIND), sorted(set(HEX_ROLES) - set(BIND))
    assert drift(TOKENS) == []
    for role in HEX_ROLES:
        assert RESOLVED[role] == DARK[role].lower(), role


def test_canvas_stays_oled_black() -> None:
    assert DARK["bg"].lower() == "#000000"
    assert BIND["bg"] == "graphite.000"


def test_neutrals_are_pure_graphite() -> None:
    roles = [
        *SURFACES,
        *TEXT_RAMP,
        "border",
        "border_ui",
        "border_hi",
        "hover",
        "pressed",
        "on_surface",
    ]
    for role in roles:
        assert BIND[role].startswith("graphite."), role
        assert _prim(role)[1] < 0.002, role
        red, green, blue = hex_to_rgb(DARK[role])
        assert red == green == blue, role


def test_surface_ladder_is_an_even_emissive_staircase() -> None:
    assert 0.13 <= _lightness("surface0") <= 0.17, "surface0 stays near-black (S5)"
    steps = [_lightness(b) - _lightness(a) for a, b in itertools.pairwise(LADDER)]
    assert all(step >= 0.04 for step in steps), steps
    assert max(steps) - min(steps) <= 0.02, f"ladder must be even: {steps}"


def test_state_surfaces_alias_the_ladder() -> None:
    assert BIND["bg_soft"] == BIND["surface0"]
    assert BIND["hover"] == BIND["selection"]
    assert BIND["pressed"] == BIND["surface2"]
    assert BIND["selection_bg"] == BIND["selection"]


def test_text_ramp_recedes_in_strict_order() -> None:
    values = [_lightness(role) for role in TEXT_RAMP]
    steps = [a - b for a, b in itertools.pairwise(values)]
    assert all(step >= 0.04 for step in steps), dict(zip(TEXT_RAMP, values, strict=True))


def test_text_is_calm_enough_for_oled_halation() -> None:
    """L12: near-white text on pure black blooms; keep AAA but pull it down."""
    assert 14.0 <= contrast(DARK["text"], DARK["bg"]) <= 16.0


def test_heading_is_brightest_but_close_to_text() -> None:
    heading = contrast(DARK["text_heading"], DARK["bg"])
    assert heading > contrast(DARK["text"], DARK["bg"])
    assert heading <= 18.2


def test_comment_stays_aaa_and_below_text() -> None:
    """AAA on bg; the nvim comment/subtle and string/comment guards set the floor near 12."""
    assert 7.0 <= contrast(DARK["comment"], DARK["bg"]) <= 12.5


def test_muted_sits_strictly_between_text_and_comment_on_the_canvas() -> None:
    text, muted, comment = (
        contrast(DARK[role], DARK["bg"]) for role in ("text", "muted", "comment")
    )
    assert text > muted > comment >= 7


def test_muted_text_holds_7_to_1_on_the_canvas() -> None:
    assert contrast(DARK["muted"], DARK["bg"]) >= 7


@pytest.mark.parametrize("role", ["comment", "subtle"])
def test_quiet_text_is_readable_on_every_quiet_surface(role: str) -> None:
    for surface in QUIET_SURFACES:
        assert contrast(DARK[role], DARK[surface]) >= 4.5, (role, surface)


def test_ui_borders_are_ordered_and_visible() -> None:
    assert _lightness("border") < _lightness("border_ui") < _lightness("border_hi")
    for role in ("border_ui", "border_hi"):
        assert contrast(DARK[role], DARK["bg"]) >= 3, role


def test_pigments_share_one_night_density() -> None:
    lightness = [_lightness(role) for role in PIGMENT_ROLES]
    assert max(lightness) - min(lightness) <= 0.01


def test_pigments_are_calm_enough_for_oled_halation() -> None:
    for role in PIGMENT_ROLES:
        assert _prim(role)[1] <= 0.13, role


@pytest.mark.parametrize("role", PIGMENT_ROLES)
def test_pigments_are_readable_on_black_and_on_selection(role: str) -> None:
    assert contrast(DARK[role], DARK["bg"]) >= 7, role
    assert contrast(DARK[role], DARK["selection"]) >= 4.5, role


def test_pigments_follow_lights_families_and_hue_order() -> None:
    for role, family in PIGMENT_FAMILIES.items():
        assert BIND[role].split(".")[0] == family, role
    hues = [_prim(role)[2] for role in PIGMENT_ROLES]
    assert hues == sorted(hues), dict(zip(PIGMENT_ROLES, hues, strict=True))
    assert abs(_prim("accent")[2] - 275) <= 5, "Dark brand sits near hue 275 (S3)"


def test_pigments_are_mutually_distinct() -> None:
    for a, b in itertools.combinations(PIGMENT_ROLES, 2):
        assert delta_e2000(DARK[a], DARK[b]) >= 12, (a, b)


def test_hover_emits_more_light_in_the_accent_family() -> None:
    accent, hover = _prim("accent"), _prim("accent_2")
    assert BIND["accent_2"].split(".")[0] == "iris"
    assert abs(accent[2] - hover[2]) <= 6
    assert hover[0] > accent[0]
    for other in ("lavender", "mauve"):
        assert delta_e2000(DARK["accent_2"], DARK[other]) >= 12, other


def test_aliased_roles_share_one_primitive() -> None:
    assert BIND["diagnostic"] == BIND["info"]
    assert BIND["sage"] == BIND["success"]
    assert BIND["link"] == BIND["accent"] == BIND["prompt_accent"]
    assert BIND["link_hover"] == BIND["accent_2"] == BIND["prompt_accent_2"]


def test_focus_ring_is_visible_on_every_surface() -> None:
    for surface in SURFACES:
        assert contrast(DARK["focus"], DARK[surface]) >= 3, surface


def test_filled_indigo_brand_keeps_its_contrast_floors() -> None:
    assert DARK["aliases"]["brand"].lower() == "#6366f1"
    guard = TOKENS["guardrails"]
    for fill in ("accent", "error", "focus"):
        on = DARK["on_" + fill] if fill != "accent" else DARK["on_accent"]
        assert contrast(on, DARK[fill]) >= 7, fill
    assert contrast(DARK["on_accent"], DARK["aliases"]["brand"]) >= 4.5
    assert apca_lc(DARK["on_accent"], DARK["accent"]) >= guard["minimum_apca_on_accent"]


def test_rgba_keys_follow_their_base_colour_with_unchanged_alpha() -> None:
    expected = {
        "panel_rgba": (DARK["surface1"], 0.92),
        "module_rgba": (DARK["text"], 0.08),
        "active_rgba": (DARK["aliases"]["brand"], 0.28),
        "inactive_border": (DARK["surface3"], 0.84),
    }
    for role, (base, alpha) in expected.items():
        assert _rgba(role) == (hex_to_rgb(base), alpha), role


def test_dark_greys_have_no_chroma_anywhere_in_the_neutral_roles() -> None:
    for role in (
        "bg",
        "surface0",
        "surface1",
        "surface2",
        "surface3",
        "selection",
        "text",
        "comment",
    ):
        assert hex_to_oklch(DARK[role])[1] < 0.002, role
