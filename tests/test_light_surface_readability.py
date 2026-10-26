"""Light-only checks of emitted text/surface pairs, not token cross-products.

The contract schema requires every matrix row to cover all three modes, and
its evaluator validates structure, not numeric contrast. These light-only
checks therefore remain local rather than claiming new contract coverage.
OpenCode includes opaque and terminal-transparent output, measured against
its actual functional surfaces (or the palette canvas for inherited fills).
"""

import copy
import json
import re
import tomllib
from pathlib import Path

import pytest

from dreamcoder_theme._math import contrast
from dreamcoder_theme.design_system import load_contract, load_tokens, render_target
from dreamcoder_theme.renderers_kitty import kitty_content
from dreamcoder_theme.renderers_opencode import opencode_content
from dreamcoder_theme.renderers_starship import starship_content
from dreamcoder_theme.renderers_tmux import tmux_content

THEME = Path(__file__).resolve().parents[1] / "DreamcoderThemes" / "dreamcoder"
TOKENS = load_tokens(THEME / "tokens.json")
LIGHT = TOKENS["modes"]["light"]
BODY = TOKENS["guardrails"]["minimum_text_contrast"]
MAIN = TOKENS["guardrails"]["preferred_main_text_contrast"]
SURFACE_PAIRS = (
    ("opencode", "text", "panel", MAIN),
    ("opencode", "muted", "panel", BODY),
    ("tmux", "text", "surface", MAIN),
)


def assert_readable(name, foreground, background, floor):
    ratio = contrast(foreground, background)
    assert ratio >= floor, f"{name}: {foreground}/{background} contrast {ratio:.3f} < {floor}"


@pytest.mark.parametrize("target,fg,bg,floor", SURFACE_PAIRS)
def test_light_surface_pairs(target, fg, bg, floor):
    contract = load_contract(THEME / "design-system.json")
    output = render_target(target, "light", LIGHT, contract["targets"][target])
    assert_readable(target, output.fields[fg], output.fields[bg], floor)

    # Public rendering of a bad palette must fail this same numeric gate.
    broken = copy.deepcopy(LIGHT)
    broken["text" if fg == "text" else "muted"] = output.fields[bg]
    output = render_target(target, "light", broken, contract["targets"][target])
    with pytest.raises(AssertionError, match=r"contrast 1\.000"):
        assert_readable(target, output.fields[fg], output.fields[bg], floor)


def opencode_pairs(content):
    theme = json.loads(content)["theme"]
    # Explicit renderer fields with associated surfaces (renderers_opencode.py).
    for fg, bg, floor in (
        ("text", "backgroundElement", MAIN),
        ("textPlaceholder", "backgroundElement", BODY),
        ("markdownCode", "markdownInlineCodeBg", BODY),
        ("diffAdded", "diffAddedBg", BODY),
        ("diffHighlightAdded", "diffAddedBg", BODY),
        ("diffRemoved", "diffRemovedBg", BODY),
        ("diffHighlightRemoved", "diffRemovedBg", BODY),
        ("diffHunkHeader", "diffHunkHeaderBg", BODY),
        ("diffFold", "diffFoldBg", BODY),
        ("syntaxFunction", "backgroundCode", BODY),
        ("syntaxMethod", "backgroundCode", BODY),
        ("syntaxOperator", "backgroundCode", BODY),
        ("syntaxDecorator", "backgroundCode", BODY),
        ("markdownCodeBlock", "markdownCodeBlockBg", MAIN),
        ("syntaxComment", "backgroundCode", BODY),
        ("syntaxString", "backgroundCode", BODY),
        ("diffContext", "diffContextBg", BODY),
        ("textAssistant", "backgroundAssistant", BODY),
        ("textUser", "backgroundUser", BODY),
        ("textTool", "backgroundTool", BODY),
    ):
        background = LIGHT["bg"] if theme[bg] == "none" else theme[bg]
        yield f"{fg}/{bg}", theme[fg], background, floor

    # Diff bodies retain code syntax highlighting, not just semantic +/- ink.
    for bg in ("diffAddedBg", "diffRemovedBg"):
        for fg in theme:
            if fg.startswith("syntax"):
                yield f"{fg}/{bg}", theme[fg], theme[bg], BODY
    for bg in ("diffAddedLineNumberBg", "diffRemovedLineNumberBg"):
        yield f"diffLineNumber/{bg}", theme["diffLineNumber"], theme[bg], BODY


def starship_pairs(content):
    doc = tomllib.loads(content)
    palette = doc["palettes"]["dreamcoder"]
    # Read text styles, not powerline separator glyphs (non-text decoration).
    for module, field in (
        ("username", "style_user"),
        ("username", "style_root"),
        ("directory", "style"),
        ("git_branch", "style"),
        ("git_status", "style"),
        ("status", "style"),
        ("cmd_duration", "style"),
        ("time", "style"),
    ):
        style = dict(re.findall(r"(fg|bg):([\w]+)", doc[module][field]))
        fg, bg = style["fg"], style.get("bg", "bg")
        yield f"{module}.{field}:{fg}/{bg}", palette[fg], palette[bg], BODY


def tmux_pairs(content):
    for line in content.splitlines():
        match = re.search(
            r"(message-style|message-command-style|mode-style|window-status-bell-style) "
            r'"fg=(#[\da-fA-F]+),bg=(#[\da-fA-F]+)',
            line,
        )
        if match:
            name, fg, bg = match.groups()
            yield name, fg, bg, MAIN if name.startswith("message") else BODY


def kitty_pairs(content):
    fields = dict(
        line.split()
        for line in content.splitlines()
        if len(line.split()) == 2 and not line.startswith("#")
    )
    for prefix in ("active_tab", "inactive_tab", "mark1", "mark2", "mark3"):
        yield prefix, fields[f"{prefix}_foreground"], fields[f"{prefix}_background"], BODY


@pytest.mark.parametrize(
    "renderer,pairs,count",
    (
        (opencode_content, opencode_pairs, 80),
        (lambda c: opencode_content(c, transparent_background=True), opencode_pairs, 80),
        (starship_content, starship_pairs, 8),
        (tmux_content, tmux_pairs, 4),
        (kitty_content, kitty_pairs, 5),
    ),
)
def test_emitted_light_surface_pairs_and_bad_output(renderer, pairs, count):
    content = renderer(LIGHT)
    measurements = list(pairs(content))
    assert len(measurements) == count  # A parser must not silently drop a style.
    for name, fg, bg, floor in measurements:
        assert_readable(name, fg, bg, floor)
        # Corrupt emitted foregrounds, then parse again: no token-only proof.
        mutated = {entry[0]: entry for entry in pairs(content.replace(fg, bg))}
        _, bad_fg, bad_bg, _ = mutated[name]
        with pytest.raises(AssertionError, match=r"contrast 1\.000"):
            assert_readable(name, bad_fg, bad_bg, floor)


@pytest.mark.parametrize("transparent", (False, True), ids=("opaque", "transparent"))
@pytest.mark.parametrize(
    "family,pairs",
    (
        ("inline", (("markdownCode", "markdownInlineCodeBg"),)),
        (
            "diff",
            (
                ("diffAdded", "diffAddedBg"),
                ("diffHighlightAdded", "diffAddedBg"),
                ("diffRemoved", "diffRemovedBg"),
                ("diffHighlightRemoved", "diffRemovedBg"),
                ("diffHunkHeader", "diffHunkHeaderBg"),
                ("diffFold", "diffFoldBg"),
            ),
        ),
        (
            "syntax",
            tuple(
                (role, "backgroundCode")
                for role in (
                    "syntaxComment",
                    "syntaxFunction",
                    "syntaxMethod",
                    "syntaxOperator",
                    "syntaxDecorator",
                )
            ),
        ),
        ("placeholder", (("textPlaceholder", "backgroundElement"),)),
    ),
)
def test_measured_light_rule_families(family, pairs, transparent):
    original = LIGHT.copy()
    theme = json.loads(opencode_content(LIGHT, transparent_background=transparent))["theme"]
    for fg, bg in pairs:
        assert_readable(f"{family}:{fg}/{bg}", theme[fg], theme[bg], BODY)
    assert original == LIGHT


@pytest.mark.parametrize("transparent", (False, True), ids=("opaque", "transparent"))
@pytest.mark.parametrize("kind", ("Added", "Removed"))
@pytest.mark.parametrize("role", ("syntax", "line-number"))
def test_light_diff_code_and_gutter(kind, role, transparent):
    theme = json.loads(opencode_content(LIGHT, transparent_background=transparent))["theme"]
    fields = (
        [key for key in theme if key.startswith("syntax")]
        if role == "syntax"
        else ["diffLineNumber"]
    )
    bg = f"diff{kind}Bg" if role == "syntax" else f"diff{kind}LineNumberBg"
    for fg in fields:
        assert_readable(f"{fg}/{bg}", theme[fg], theme[bg], BODY)
    # Preserve the health check's canvas distinction floor alongside text contrast.
    canvas = LIGHT["bg"] if theme["background"] == "none" else theme["background"]
    assert_readable(f"{bg}/canvas", theme[bg], canvas, 1.05)
    # Body and gutter share a tint, with distinct addition/removal identities.
    assert theme["diffAddedBg"] != theme["diffRemovedBg"]
    assert theme[f"diff{kind}Bg"] == theme[f"diff{kind}LineNumberBg"]


@pytest.mark.parametrize("target", ("kitty", "ghostty", "warp", "starship", "tmux", "opencode"))
def test_existing_main_and_selection_pairs_remain_readable(target):
    contract = load_contract(THEME / "design-system.json")
    output = render_target(target, "light", LIGHT, contract["targets"][target])
    assert_readable(target, output.fields["text"], output.fields["background"], MAIN)
    if "selection.text" in output.fields:
        assert_readable(
            target + ":selection",
            output.fields["selection.text"],
            output.fields["selection.background"],
            TOKENS["guardrails"]["minimum_terminal_selection_contrast"],
        )
