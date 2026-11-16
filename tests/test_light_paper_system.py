"""Dreamcoder Light "Lucuma paper" system rules (odd/tasks/dreamcoder-light-paper.md)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from dreamcoder_theme._math import contrast, hex_to_rgb, rel_luminance

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"

RESTING = ("bg", "bg_soft", "surface0", "surface1", "surface2", "selection")
TEXT = (
    "text",
    "muted",
    "subtle",
    "comment",
    "border_ui",
    "accent",
    "accent_2",
    "error",
    "warning",
    "success",
    "info",
    "focus",
    "lavender",
    "mauve",
)
NEUTRALS = ("bg", "bg_soft", "surface0", "surface1", "surface2", "surface3", "text", "muted")


def _light() -> dict[str, str]:
    return json.loads(TOKENS.read_text())["modes"]["light"]


def _oklch(value: str) -> tuple[float, float, float]:
    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(x / 255) for x in hex_to_rgb(value))
    lms = (
        0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
        0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
        0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b,
    )
    l_, m_, s_ = (x ** (1 / 3) for x in lms)
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lightness, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


@pytest.mark.parametrize("fg", TEXT)
def test_text_tokens_read_on_every_resting_surface(fg: str) -> None:
    light = _light()
    for surface in RESTING:
        assert contrast(light[fg], light[surface]) >= 4.5, (fg, surface)


def test_borders_reach_component_contrast() -> None:
    light = _light()
    for surface in ("bg", "bg_soft", "surface0", "surface1"):
        assert contrast(light["border"], light[surface]) >= 3.0, surface


def test_neutrals_are_paper_not_sepia() -> None:
    light = _light()
    for key in NEUTRALS:
        assert _oklch(light[key])[1] <= 0.02, key


def test_warning_is_not_confusable_with_the_accent() -> None:
    light = _light()
    gap = abs(_oklch(light["warning"])[2] - _oklch(light["accent"])[2])
    assert min(gap, 360 - gap) >= 25


def test_elevation_ladder_and_visible_selection() -> None:
    light = _light()
    lum = {k: rel_luminance(light[k]) for k in ("bg_soft", "bg", "surface0", "surface1")}
    assert lum["bg_soft"] < lum["bg"] < lum["surface0"]
    assert lum["surface1"] < lum["bg"]
    for surface in ("bg", "bg_soft", "surface0"):
        assert contrast(light["selection"], light[surface]) >= 1.15, surface
