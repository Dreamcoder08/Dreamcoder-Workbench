"""Protect Dark terminal color roles without changing canonical theme tokens."""

from __future__ import annotations

import colorsys
import json
import re
from pathlib import Path

import pytest

from dreamcoder_theme.palette import ansi, contrast, rel_luminance
from dreamcoder_theme.renderers_ghostty_warp import ghostty_content, warp_content
from dreamcoder_theme.renderers_kitty import kitty_content

ROOT = Path(__file__).resolve().parents[1]
MODES = json.loads((ROOT / "DreamcoderThemes/dreamcoder/tokens.json").read_text())["modes"]

# Captured from the pending-state baseline before this Dark-only change.
BASELINE = {
    "dark": (
        "#797979",
        "#FB8585",
        "#34D399",
        "#FBBF24",
        "#7DD3FC",
        "#D8B4FE",
        "#D4B5FD",
        "#C7C7C7",
        "#A7A7A7",
        "#f79696",
        "#54d6a7",
        "#f7c647",
        "#90d6f8",
        "#dbbdfa",
        "#5a94f3",
        "#E6E6E6",
    ),
    "light": (
        "#5e5c57",
        "#842f24",
        "#315b31",
        "#654300",
        "#0d4a68",
        "#7d3e64",
        "#57478b",
        "#352e22",
        "#554638",
        "#985145",
        "#456042",
        "#7f6128",
        "#36677d",
        "#784c64",
        "#2e666b",
        "#17120d",
    ),
    "dusk": (
        "#595753",
        "#773126",
        "#344f30",
        "#604000",
        "#104b67",
        "#784762",
        "#5b4e86",
        "#4c443a",
        "#5a4f43",
        "#8c5146",
        "#556a4e",
        "#795e27",
        "#37677b",
        "#745162",
        "#39696d",
        "#1a1713",
    ),
}


def _hue(color: str) -> float:
    channels = tuple(int(color[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hsv(*channels)[0] * 360


def test_dark_cyan_roles_are_distinct_and_readable() -> None:
    palette = MODES["dark"]
    slots = ansi(palette)

    assert slots[6] == "#58d3ca"
    assert slots[14] == "#6dd6ce"
    for index in (6, 14):
        red, green, blue = (int(slots[index][i : i + 2], 16) for i in (1, 3, 5))
        assert green > red and blue > red
        assert contrast(slots[index], palette["bg"]) >= 4.5
        separation = abs(_hue(slots[index]) - _hue(slots[5]))
        assert min(separation, 360 - separation) > 60
    assert rel_luminance(slots[14]) > rel_luminance(slots[6])


def test_dark_other_ansi_slots_remain_unchanged() -> None:
    slots = ansi(MODES["dark"])
    assert {i: color for i, color in enumerate(slots) if i not in (6, 14)} == {
        i: color for i, color in enumerate(BASELINE["dark"]) if i not in (6, 14)
    }


@pytest.mark.parametrize("mode", ("light", "dusk"))
def test_non_dark_ansi_slots_are_identical_to_baseline(mode: str) -> None:
    assert tuple(ansi(MODES[mode])) == BASELINE[mode]


@pytest.mark.parametrize(
    ("path", "renderer", "pattern"),
    (
        (
            "DreamcoderKitty/.config/kitty/colors-dreamcoder-dark.conf",
            kitty_content,
            r"(?m)^color(\d+)\s+(#[0-9a-fA-F]{6})$",
        ),
        (
            "DreamcoderGhostty/.config/ghostty/themes/dreamcoder-dark",
            ghostty_content,
            r"(?m)^palette = (\d+)=(#[0-9a-fA-F]{6})$",
        ),
        (
            "DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder-Dark.yaml",
            warp_content,
            r"(?m)^    cyan: '(#[0-9a-fA-F]{6})'$",
        ),
    ),
)
def test_dark_terminal_variants_render_the_same_cyan_slots(path, renderer, pattern) -> None:
    palette = MODES["dark"]
    rendered = renderer(palette)
    assert (ROOT / path).read_text() == rendered
    matches = re.findall(pattern, rendered)
    if "Warp" in path:
        assert matches == ["#58d3ca", "#6dd6ce"]
    else:
        indexed = {int(index): color for index, color in matches}
        assert indexed[6] == "#58d3ca"
        assert indexed[14] == "#6dd6ce"
