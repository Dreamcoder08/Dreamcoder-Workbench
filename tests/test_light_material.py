"""Dreamcoder Light material laws: paper, ink and pigment.

Spec: odd/tasks/dreamcoder-light-coherence.md, T3 (S2, S3, S6).

The values live in tokens.json; these tests hold the physical model they must
obey, so a future edit cannot drift out of the system silently.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import apca_lc, contrast
from dreamcoder_theme.color_space import delta_e2000, parse_oklch

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "DreamcoderThemes/dreamcoder/tokens.json").read_text(encoding="utf-8"))
LIGHT = TOKENS["modes"]["light"]
PRIMS = TOKENS["primitives"]["light"]
BIND = TOKENS["bindings"]["light"]
TEXT_SURFACES = ("bg", "bg_soft", "surface0", "surface1", "surface2")
PIGMENT_ROLES = ("error", "accent", "warning", "success", "focus", "info", "lavender", "mauve")


def _family(name: str) -> list[tuple[float, float, float]]:
    """OKLCH of one primitive family, lightest first."""
    rows = [parse_oklch(v) for k, v in PRIMS.items() if k.split(".")[0] == name]
    return sorted(rows, reverse=True)


def test_delta_e2000_matches_sharma_reference_pairs() -> None:
    # Sharma, Wu & Dalal (2005), Table 1, pairs 1, 7 and 17.
    assert delta_e2000((50, 2.6772, -79.7751), (50, 0, -82.7485)) == pytest.approx(2.0425, abs=1e-4)
    assert delta_e2000((50, 0, 0), (50, -1, 2)) == pytest.approx(2.3669, abs=1e-4)
    assert delta_e2000((50, 2.5, 0), (73, 25, -18)) == pytest.approx(27.1492, abs=1e-4)


def test_paper_darkens_like_aging_cellulose() -> None:
    """Lignin chromophores: deeper paper is more chromatic and drifts toward red."""
    paper = _family("paper")
    assert len(paper) >= 5
    for (_, c_hi, h_hi), (_, c_lo, h_lo) in itertools.pairwise(paper):
        assert c_lo > c_hi, "paper chroma must rise as lightness falls"
        assert h_lo <= h_hi + 0.5, "paper hue must not swing back toward yellow"
    assert all(70 <= h <= 84 for _, _, h in paper)


@pytest.mark.parametrize("family", ["ink", "clay"])
def test_family_shares_one_hue_axis(family: str) -> None:
    hues = [h for _, _, h in _family(family)]
    assert max(hues) - min(hues) <= 2.0


def test_ink_steps_are_perceptually_distinct() -> None:
    ink = [lightness for lightness, _, _ in _family("ink")]
    assert all(a - b >= 0.05 for a, b in itertools.pairwise(ink))


def test_clay_is_an_umber_wash_over_paper() -> None:
    """A thinner wash is lighter and less chromatic (Kubelka-Munk)."""
    clay = _family("clay")
    assert all(c_lo > c_hi for (_, c_hi, _), (_, c_lo, _) in itertools.pairwise(clay))


def test_pigments_share_one_ink_density() -> None:
    lightness = [parse_oklch(PRIMS[BIND[role]])[0] for role in PIGMENT_ROLES]
    assert max(lightness) - min(lightness) <= 0.01


def test_pigments_are_mutually_distinct() -> None:
    for a, b in itertools.combinations(PIGMENT_ROLES, 2):
        assert delta_e2000(LIGHT[a], LIGHT[b]) >= 12, (a, b)


def test_aliased_roles_share_one_primitive() -> None:
    assert BIND["diagnostic"] == BIND["info"]
    assert BIND["sage"] == BIND["success"]


def test_hover_accent_stays_in_the_accent_family() -> None:
    accent_hue = parse_oklch(PRIMS[BIND["accent"]])[2]
    hover_hue = parse_oklch(PRIMS[BIND["accent_2"]])[2]
    assert abs(accent_hue - hover_hue) <= 6
    assert delta_e2000(LIGHT["accent_2"], LIGHT["error"]) >= 12


@pytest.mark.parametrize("role", [*PIGMENT_ROLES, "accent_2", "subtle", "comment"])
def test_readable_on_every_text_surface(role: str) -> None:
    for surface in TEXT_SURFACES:
        assert contrast(LIGHT[role], LIGHT[surface]) >= 4.5, (role, surface)
    assert apca_lc(LIGHT[role], LIGHT["bg"]) >= 75
