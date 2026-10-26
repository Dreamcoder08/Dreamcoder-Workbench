"""T1/S1-S2: emitted Dark states, not token cross-products or live UI proof.

Rofi/Waybar alpha surfaces need a known compositor background; Matugen bridges
only define colors. Herdr profiles establish schema, not exact text pairing.
None of these establishes ownership of the user's screenshot sidebar.
"""

import configparser
import json
import re
import tomllib
from hashlib import sha256
from pathlib import Path

import pytest

from dreamcoder_theme.herdr_contract import SUPPORTED_PROFILES
from dreamcoder_theme.palette import apca_lc, contrast, load_guardrails
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_extra_notify import dunst_content
from dreamcoder_theme.renderers_ghostty_warp import ghostty_content
from dreamcoder_theme.renderers_herdr import herdr_content
from dreamcoder_theme.renderers_hypr_waybar_rofi import rofi_content, waybar_content
from dreamcoder_theme.renderers_kitty import kitty_content
from dreamcoder_theme.renderers_pi import pi_theme_content
from dreamcoder_theme.renderers_starship import starship_content
from dreamcoder_theme.renderers_tmux import tmux_content

DARK = VARIANTS["dark"]
GUARDS = load_guardrails(
    Path(__file__).resolve().parents[1] / "DreamcoderThemes/dreamcoder/tokens.json"
)


def _hex(value):
    assert re.fullmatch(r"#[0-9a-fA-F]{6}", value), f"unresolved color: {value!r}"
    return value


def _check(rows):
    failures = []
    for label, fg, bg, floor in rows:
        ratio = contrast(_hex(fg), _hex(bg))
        if ratio < floor:
            failures.append(f"{label}: {fg}/{bg} WCAG={ratio:.3f} < {floor}")
    assert not failures, "\n".join(failures)


def terminal_pairs():
    # renderers_kitty.py:16-60; renderers_ghostty_warp.py:16-22.
    kitty = dict(re.findall(r"^(\w+)\s+(#[\da-fA-F]{6})$", kitty_content(DARK), re.M))
    ghost = dict(re.findall(r"^([\w-]+) = (#[\da-fA-F]{6})$", ghostty_content(DARK), re.M))
    assert len(kitty) == 39 and len(ghost) == 6
    rows = []
    for label, data, pairs in (
        (
            "kitty",
            kitty,
            (
                ("foreground", "background"),
                ("active_tab_foreground", "active_tab_background"),
                ("inactive_tab_foreground", "inactive_tab_background"),
                ("cursor_text_color", "cursor"),
                *((f"mark{i}_foreground", f"mark{i}_background") for i in range(1, 4)),
                ("selection_foreground", "selection_background"),
            ),
        ),
        (
            "ghostty",
            ghost,
            (
                ("foreground", "background"),
                ("cursor-text", "cursor-color"),
                ("selection-foreground", "selection-background"),
            ),
        ),
    ):
        for fg, bg in pairs:
            floor = (
                GUARDS["minimum_terminal_selection_contrast"]
                if "selection" in fg
                else GUARDS["minimum_text_contrast"]
            )
            rows.append((f"{label}.{fg}/{bg}", data[fg], data[bg], floor))
    assert len(rows) == 11
    return rows


def pi_pairs():
    # renderers_pi.py:15-20,49-76: empty foreground inherits terminal text.
    theme = json.loads(pi_theme_content(DARK))
    colors, variables = theme["colors"], theme["vars"]
    terminal = dict(re.findall(r"^(\w+)\s+(#[\da-fA-F]{6})$", kitty_content(DARK), re.M))

    def resolve(value):
        seen = set()
        while value in variables:
            assert value not in seen, f"cyclic Pi variable: {value}"
            seen.add(value)
            value = variables[value]
        return _hex(value or terminal["foreground"])

    assert len(colors) == 51 and len(variables) == 12
    rows = []
    associations = {
        "terminal": ("text", "thinkingText", "muted", "dim", "mdLink", "syntaxComment"),
        "selectedBg": ("text",),
        "userMessageBg": ("userMessageText",),
        "customMessageBg": ("customMessageText", "customMessageLabel"),
        "toolPendingBg": ("toolTitle", "toolOutput", "toolDiffContext"),
        "toolSuccessBg": ("toolTitle", "toolOutput", "toolDiffContext"),
        "toolErrorBg": ("toolTitle", "toolOutput", "toolDiffContext", "error"),
    }
    for surface, roles in associations.items():
        bg = terminal["background"] if surface == "terminal" else resolve(colors[surface])
        for role in roles:
            rows.append(
                (f"pi.{role}/{surface}", resolve(colors[role]), bg, GUARDS["minimum_text_contrast"])
            )
    assert len(rows) == 20
    return rows


def tmux_pairs():
    # renderers_tmux.py:48-84: tab styles inherit status-style background.
    styles = dict(re.findall(r'^(?:set|setw) -g ([\w-]+) "([^"]*)"$', tmux_content(DARK), re.M))
    bar = re.search(r"bg=(#[\da-fA-F]{6})", styles["status-style"])[1]
    rows = []
    for name in (
        "window-status-style",
        "window-status-current-style",
        "message-style",
        "message-command-style",
        "mode-style",
        "window-status-bell-style",
    ):
        fields = dict(re.findall(r"(fg|bg)=(#[\da-fA-F]{6})", styles[name]))
        rows.append(
            (f"tmux.{name}", fields["fg"], fields.get("bg", bar), GUARDS["minimum_text_contrast"])
        )
    for name in ("status-left", "status-right"):
        foregrounds = re.findall(r"fg=(#[\da-fA-F]{6})", styles[name])
        assert len(foregrounds) == 2
        rows.extend(
            (f"tmux.{name}.{i}", fg, bar, GUARDS["minimum_text_contrast"])
            for i, fg in enumerate(foregrounds)
        )
    assert len(rows) == 10
    return rows


def starship_pairs():
    # renderers_starship.py:86-197: only text styles, not powerline separators.
    theme = tomllib.loads(starship_content(DARK))
    palette = theme["palettes"][theme["palette"]]
    styles = []
    for name, module in theme.items():
        if isinstance(module, dict) and name not in {"palettes", "custom"}:
            styles.extend(
                (f"{name}.{key}", value)
                for key, value in module.items()
                if key.startswith("style") or (name == "character" and key.endswith("_symbol"))
            )
    styles.append(("custom.ai_session.style", theme["custom"]["ai_session"]["style"]))
    assert len(styles) == 18
    rows, unresolved = [], []
    for label, style in styles:
        fields = dict(re.findall(r"(fg|bg):([\w_]+)", style))
        assert "fg" in fields, label
        fg, bg = fields["fg"], fields.get("bg", "bg")
        if fg not in palette or bg not in palette:
            unresolved.append(f"{label}: fg:{fg} bg:{bg}")
        else:
            rows.append(
                (f"starship.{label}", palette[fg], palette[bg], GUARDS["minimum_text_contrast"])
            )
    assert len(rows) + len(unresolved) == 18
    return rows, unresolved


def dunst_pairs():
    # renderers_extra_notify.py:26-42: notification foreground on urgency fill.
    parsed = configparser.ConfigParser()
    parsed.read_string(dunst_content(DARK))
    assert parsed.sections() == ["urgency_low", "urgency_normal", "urgency_critical"]
    return [
        (
            f"dunst.{name}.foreground/background",
            parsed[name]["foreground"].strip('"'),
            parsed[name]["background"].strip('"'),
            GUARDS["minimum_text_contrast"],
        )
        for name in parsed.sections()
    ]


@pytest.mark.parametrize("pairs", [terminal_pairs, pi_pairs, tmux_pairs, dunst_pairs])
def test_emitted_dark_text_pairs(pairs):
    _check(pairs())


def test_starship_emitted_text_pairs():
    rows, unresolved = starship_pairs()
    _check(rows)
    assert not unresolved, "Unresolved emitted Starship colors: " + "; ".join(unresolved)
    assert len(rows) == 18
    palette = tomllib.loads(starship_content(DARK))["palettes"]["dreamcoder"]
    light_palette = tomllib.loads(starship_content(VARIANTS["light"]))["palettes"]["dreamcoder"]
    assert set(palette) == set(light_palette) | {"diag"}
    assert palette["diag"] == palette["diagnostic"] == DARK["diagnostic"]


@pytest.mark.parametrize(
    "mode, expected",
    [
        ("light", "93f971c4ad02eef751a3e169f5f8e4a796c0910310bdeb8a90d610e174553b1e"),
        ("dusk", "581c6c4b0b90ea880c2cd94af6cffd1f660b45555a07c037af1f8128679340df"),
    ],
)
def test_starship_non_dark_output_preserved(mode, expected):
    output = starship_content(VARIANTS[mode])
    # Fixed pre-fix bytes: no history access, extra aliases, or blank lines.
    assert sha256(output.encode()).hexdigest() == expected
    theme = tomllib.loads(output)
    palette = theme["palettes"][theme["palette"]]
    assert "diag" not in palette
    assert palette["diagnostic"] == VARIANTS[mode]["diagnostic"]
    for module in (
        theme["python"],
        theme["golang"],
        theme["docker_context"],
        theme["custom"]["ai_session"],
    ):
        assert module["style"] == "fg:diag bold"


def test_pi_quiet_text_apca_on_emitted_surfaces():
    for label, fg, bg, _ in pi_pairs():
        if any(
            f"pi.{role}/" in label
            for role in ("thinkingText", "muted", "dim", "syntaxComment", "toolDiffContext")
        ):
            assert abs(apca_lc(fg, bg)) >= GUARDS["minimum_apca_quiet"], label


def test_one_to_one_mutation_is_rejected():
    row = terminal_pairs()[0]
    with pytest.raises(AssertionError, match=r"WCAG=1\.000"):
        _check([(row[0], row[2], row[2], row[3])])


def test_optional_outputs_retain_explicit_proof_boundaries():
    # No guessed wallpaper compositing; borders/focus are not body text.
    for output in (rofi_content(DARK), waybar_content(DARK)):
        assert DARK["panel_rgba"] in output
        assert DARK["active_rgba"] in output
    assert len(SUPPORTED_PROFILES) == 7
    for profile in SUPPORTED_PROFILES:
        custom = tomllib.loads(herdr_content(profile, "dark", DARK))["theme"]["custom"]
        assert set(custom) == set(profile.evidence.allowed_custom_fields)
        assert len(custom) in (16, 19)
        for value in custom.values():
            _hex(value)
