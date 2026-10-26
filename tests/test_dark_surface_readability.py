"""Dark emitted text/surface regressions; no speculative token cross-product."""

import json

import pytest

from dreamcoder_theme.palette import apca_lc, contrast
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_opencode import opencode_content, opencode_tokens

DARK = VARIANTS["dark"]


def readable(theme, fg, bg, floor=4.5):
    background = DARK["bg"] if theme[bg] == "none" else theme[bg]
    ratio = contrast(theme[fg], background)
    assert ratio >= floor, f"{fg}/{bg}: {ratio:.3f} < {floor}"


@pytest.fixture(params=(False, True), ids=("opaque", "transparent"))
def theme(request):
    original = DARK.copy()
    result = json.loads(opencode_content(DARK, request.param))["theme"]
    assert original == DARK
    return result


def test_dark_inline_code_preserves_sage_on_subtle_fill(theme):
    assert theme["markdownCode"] == DARK["sage"]
    readable(theme, "markdownCode", "markdownInlineCodeBg")
    readable(theme, "markdownInlineCodeBg", "background", 1.05)


@pytest.mark.parametrize("kind", ("Added", "Removed"))
def test_dark_diff_semantics_syntax_and_gutter(theme, kind):
    bg = f"diff{kind}Bg"
    fields = [key for key in theme if key.startswith("syntax")]
    assert len(fields) == 29
    fields += [f"diff{kind}", f"diffHighlight{kind}", "diffLineNumber"]
    failures = [
        (fg, contrast(theme[fg], theme[bg]))
        for fg in fields
        if contrast(theme[fg], theme[bg]) < 4.5
    ]
    assert not failures, failures
    assert theme[bg] == theme[f"diff{kind}LineNumberBg"]
    assert theme["diffAddedBg"] != theme["diffRemovedBg"]
    # Retain green/red identity as well as the app's existing +/- markers.
    channels = tuple(int(theme[bg][i : i + 2], 16) for i in (1, 3, 5))
    assert channels[1 if kind == "Added" else 0] == max(channels)
    for surface in (bg, f"diff{kind}LineNumberBg", "diffHunkHeaderBg"):
        readable(theme, surface, "background", 1.05)
        assert contrast(theme[surface], DARK["bg"]) <= 2.4
    readable(theme, "diffHunkHeader", "diffHunkHeaderBg")


def test_dark_existing_main_messages_and_selection(theme):
    assert theme["background"] in ("none", "#000000")
    for bg in (
        "background",
        "backgroundPanel",
        "backgroundElement",
        "backgroundCode",
        "backgroundAssistant",
        "backgroundUser",
        "backgroundTool",
    ):
        readable(theme, "text", bg, 7.0)
    for role in ("Assistant", "User", "Tool"):
        readable(theme, f"text{role}", f"background{role}")
    readable(theme, "textSelected", "backgroundSelected", 7.0)
    assert abs(apca_lc(theme["text"], DARK["bg"])) >= 50
    tokens = opencode_tokens(DARK)
    for field, token in (
        ("syntaxKeyword", "keyword"),
        ("syntaxTag", "keyword"),
        ("syntaxDeprecated", "deprecated"),
    ):
        assert theme[field] == tokens[token]
    for surface in ("backgroundElement", "backgroundCode", "backgroundLine"):
        readable(theme, surface, "background", 1.05)
