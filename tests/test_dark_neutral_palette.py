"""Regression coverage for the Dreamcoder Dark neutral hierarchy."""

import json
from pathlib import Path

import pytest

from dreamcoder_theme.palette import (
    apca_lc,
    contrast,
    load_guardrails,
)

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"


def _dark() -> dict[str, str]:
    return json.loads(TOKENS.read_text(encoding="utf-8"))["modes"]["dark"]


def test_dark_uses_the_authorized_neutral_surface_ladder():
    dark = _dark()

    assert {
        key: dark[key] for key in ("bg", "bg_soft", "surface0", "surface1", "surface2", "surface3")
    } == {
        "bg": "#000000",
        "bg_soft": "#0B0B0B",
        "surface0": "#0B0B0B",
        "surface1": "#0D0D0F",
        "surface2": "#1F1F1F",
        "surface3": "#2E2E2E",
    }
    assert dark["selection"] == dark["selection_bg"] == dark["hover"] == "#3A3A3A"
    assert dark["pressed"] == dark["surface2"]


def test_dark_neutral_text_mirrors_remain_legible_on_raised_roles():
    dark = _dark()

    assert dark["text"] == dark["prompt_text"] == dark["on_surface"] == "#E6E6E6"
    assert dark["muted"] == dark["prompt_muted"] == "#C7C7C7"
    assert dark["subtle"] == dark["disabled"] == "#A7A7A7"
    assert dark["comment"] == "#D0D0D0"
    assert contrast(dark["text"], dark["surface3"]) >= 10
    assert contrast(dark["selection_fg"], dark["selection_bg"]) >= 7


@pytest.mark.parametrize(
    ("role", "surface", "minimum"),
    (
        ("muted", "surface3", 7.0),
        ("subtle", "surface2", 4.5),
        ("comment", "surface2", 7.0),
        ("accent", "surface2", 4.5),
        ("error", "surface2", 4.5),
        ("warning", "surface2", 4.5),
        ("success", "surface2", 4.5),
        ("diagnostic", "surface2", 4.5),
        ("sage", "surface2", 4.5),
        ("lavender", "surface2", 4.5),
        ("mauve", "surface2", 4.5),
    ),
)
def test_dark_rendered_text_roles_remain_legible_on_their_raised_surfaces(
    role: str, surface: str, minimum: float
):
    """Check real text-bearing roles, not decorative borders or disabled state."""
    dark = _dark()

    assert contrast(dark[role], dark[surface]) >= minimum


@pytest.mark.parametrize(
    ("role", "guardrail"),
    (
        ("muted", "minimum_apca_quiet"),
        ("subtle", "minimum_apca_quiet"),
        ("comment", "minimum_apca_quiet"),
        ("error", "minimum_apca_body_dark"),
        ("warning", "minimum_apca_body_dark"),
        ("success", "minimum_apca_body_dark"),
        ("info", "minimum_apca_body_dark"),
        ("diagnostic", "minimum_apca_body_dark"),
    ),
)
def test_dark_roles_meet_their_declared_apca_thresholds(role: str, guardrail: str):
    dark = _dark()
    thresholds = load_guardrails(TOKENS)

    assert abs(apca_lc(dark[role], dark["bg"])) >= thresholds[guardrail]
