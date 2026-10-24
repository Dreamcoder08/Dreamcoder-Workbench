"""Regression coverage for the Dreamcoder Dark neutral hierarchy."""

import hashlib
import json
from pathlib import Path

import pytest

from dreamcoder_theme.palette import (
    adaptive_palette,
    apca_lc,
    contrast,
    load_guardrails,
)
from dreamcoder_theme.palette_tokens import VARIANTS

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"


def _dark() -> dict[str, str]:
    return json.loads(TOKENS.read_text(encoding="utf-8"))["modes"]["dark"]


@pytest.fixture
def wallpaper_scheme(monkeypatch):
    """Non-neutral input without invoking Matugen or reading a wallpaper."""
    scheme = {
        "background": "#cc6699",
        "surface_container": "#996633",
        "surface_container_high": "#663399",
        "surface_variant": "#339966",
        "primary": "#22cc88",
        "secondary": "#ff8844",
        "tertiary": "#cc88ff",
        "outline": "#997755",
        "primary_container": "#445577",
    }
    monkeypatch.setattr("dreamcoder_theme.palette.matugen_scheme", lambda *args: scheme)
    return scheme


def test_adaptive_dark_preserves_black_canvas_and_neutral_surfaces(wallpaper_scheme):
    base = VARIANTS["dark"].copy()
    original = base.copy()

    adaptive = adaptive_palette(base, "dark", Path("unused-wallpaper.png"), True)

    assert adaptive["bg"] == "#000000"
    for key in ("bg_soft", "surface0", "surface1", "surface2", "surface3"):
        assert adaptive[key] == base[key]
        assert adaptive[key] != adaptive["bg"]
    for key in ("accent", "accent_2", "diagnostic"):
        assert adaptive[key] != base[key]
        assert contrast(adaptive[key], adaptive["bg"]) >= 4.5
    assert adaptive["prompt_accent"] == adaptive["accent"]
    assert adaptive["prompt_accent_2"] == adaptive["accent_2"]
    assert base == original


@pytest.mark.parametrize("mode", ("light", "dusk"))
def test_adaptive_light_modes_remain_unchanged(mode, wallpaper_scheme):
    adaptive = adaptive_palette(VARIANTS[mode], mode, Path("unused-wallpaper.png"), True)
    fingerprint = hashlib.sha256(json.dumps(adaptive, sort_keys=True).encode()).hexdigest()

    # Full-output snapshots captured before the Dark-only policy fix.
    assert (
        fingerprint
        == {
            "light": "7c097a3ec73a027b444d0bce49cc01864e2f21f34a5c2f4697c68ddb78a979f1",
            "dusk": "4489a603fff0e4131bd0379426d288b8ebcc59e3281d864fe8131b5b3556160e",
        }[mode]
    )


@pytest.mark.parametrize("mode", ("dark", "light", "dusk"))
def test_adaptive_palette_without_scheme_preserves_base(mode, monkeypatch):
    monkeypatch.setattr("dreamcoder_theme.palette.matugen_scheme", lambda *args: {})
    base = VARIANTS[mode].copy()

    assert adaptive_palette(base, mode, Path("unused-wallpaper.png"), False) == base


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
