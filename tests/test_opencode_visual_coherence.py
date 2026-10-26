"""OpenCode-only surface hierarchy and readable secondary text."""

import json
from pathlib import Path

import pytest

from dreamcoder_theme.palette import contrast, detect_mode, guard, mix
from dreamcoder_theme.renderers_opencode import opencode_content

TOKENS_FILE = Path(__file__).resolve().parents[1] / "DreamcoderThemes/dreamcoder/tokens.json"
VARIANTS = json.loads(TOKENS_FILE.read_text())["modes"]


@pytest.fixture(params=list(VARIANTS))
def palette(request):
    return VARIANTS[request.param].copy()


def test_transparent_panel_inherits_terminal_canvas(palette):
    theme = json.loads(opencode_content(palette, transparent_background=True))["theme"]
    assert theme["background"] == "none"
    assert theme["backgroundPanel"] == "none"


@pytest.mark.parametrize(
    "role",
    ["backgroundElement", "backgroundCode", "backgroundLine", "markdownCodeBlockBg", "diffFoldBg"],
)
def test_transparent_functional_surfaces_use_canonical_soft_background(palette, role):
    theme = json.loads(opencode_content(palette, transparent_background=True))["theme"]
    assert theme[role] == palette["bg_soft"]


@pytest.mark.parametrize("role", ["text", "textMuted", "textSubtle", "textPlaceholder"])
@pytest.mark.parametrize(
    "surface", ["background", "backgroundPanel", "backgroundElement", "backgroundCode"]
)
def test_transparent_text_is_readable_on_each_surface(palette, role, surface):
    theme = json.loads(opencode_content(palette, transparent_background=True))["theme"]
    background = palette["bg"] if theme[surface] == "none" else theme[surface]
    assert contrast(theme[role], background) >= 4.5


@pytest.mark.parametrize(
    "token,role", [("muted", "textMuted"), ("subtle", "textSubtle"), ("comment", "textPlaceholder")]
)
def test_transparent_secondary_text_is_guarded_without_changing_palette(palette, token, role):
    palette[token] = palette["bg_soft"]
    original = palette.copy()
    theme = json.loads(opencode_content(palette, transparent_background=True))["theme"]
    for background in (palette["bg"], palette["bg_soft"]):
        assert contrast(theme[role], background) >= 4.5
    assert palette == original


def test_transparent_hover_selection_and_syntax_are_preserved(palette):
    opaque = json.loads(opencode_content(palette))
    transparent = json.loads(opencode_content(palette, transparent_background=True))
    assert transparent.keys() == opaque.keys()
    assert transparent["defs"] == opaque["defs"]
    assert transparent["theme"].keys() == opaque["theme"].keys()
    for key, value in opaque["theme"].items():
        corrected = detect_mode(palette) == "light" and key in (
            "syntaxComment",
            "syntaxFunction",
            "syntaxMethod",
            "syntaxOperator",
            "syntaxDecorator",
        )
        if corrected:
            assert transparent["theme"][key] == guard(
                value,
                transparent["theme"]["backgroundCode"],
                "light",
                minimum=4.5,
            )
        elif key.startswith("syntax") or key in (
            "backgroundHover",
            "backgroundSelected",
            "textSelected",
        ):
            assert transparent["theme"][key] == value
    assert transparent["theme"]["backgroundHover"] != palette["bg_soft"]
    assert transparent["theme"]["backgroundSelected"] != palette["bg_soft"]


def test_nontransparent_surface_and_text_formulas_are_preserved(palette):
    theme = json.loads(opencode_content(palette))["theme"]
    dark = detect_mode(palette) == "dark"
    assert theme["background"] == palette["bg"]
    assert theme["backgroundPanel"] == palette["surface1" if dark else "surface0"]
    assert theme["backgroundElement"] == (
        palette["surface1"] if dark else mix(palette["bg_soft"], palette["surface1"], 0.4)
    )
    assert theme["backgroundCode"] == palette["surface1" if dark else "surface0"]
    assert theme["backgroundLine"] == palette["surface1" if dark else "bg_soft"]
    assert theme["text"] == palette["text"]
    assert theme["textMuted"] == palette["muted"]
    assert theme["textSubtle"] == guard(
        palette["subtle"], palette["bg"], detect_mode(palette), minimum=5.5
    )
    assert theme["textPlaceholder"] == (
        palette["comment"]
        if dark
        else guard(
            palette["comment"],
            theme["backgroundElement"],
            "light",
            minimum=4.5,
        )
    )
