"""Light semantic chrome: badges, tiles, window borders and shell blocks share one rule.

Spec: odd/tasks/dreamcoder-light-coherence.md, T9 (S2, S6); design in L14.

Pigment wash rule (Kubelka-Munk thin layer): a coloured chip, badge or tile is a
pigment at ~12-16% over paper as fill and the same pigment as text or icon. Light
chrome has no saturated solid fills and no dark surface leaking into the paper.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from dreamcoder_theme._math import contrast, mix
from dreamcoder_theme.color_space import hex_to_oklch
from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_gentle_shell import (
    gentle_shell_theme_content,
    gentle_shell_tokens,
)
from dreamcoder_theme.renderers_hypr_waybar_rofi import hypr_content, waybar_content
from dreamcoder_theme.renderers_pi import pi_theme_content

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
THEMES = ROOT / "DreamcoderThemes/dreamcoder"
LIVE_OVERRIDE = ROOT / "DreamcoderWaybar/.config/waybar/style-custom.css"
WASH_ALPHA_MAX = 0.16
DARKEST_FILL_L = 0.80
TEXT_MIN = 4.5
# Selectors that are chips, badges or tiles (never workspace buttons or bar modules).
CHIP_SELECTORS = ("#custom-updates",)


def _variants() -> dict[str, dict[str, str]]:
    return load_variants(VARIANTS, TOKENS)


@pytest.fixture(scope="module")
def light() -> dict[str, str]:
    return _variants()["light"]


@pytest.fixture(scope="module")
def dark() -> dict[str, str]:
    return _variants()["dark"]


# ── Waybar ──────────────────────────────────────────────────────────────────


def _rules(css: str) -> list[tuple[list[str], dict[str, str]]]:
    """(selectors, declarations) per rule, comments stripped."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    for selector_text, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        selectors = [s.strip() for s in selector_text.split(",") if s.strip()]
        decls = {}
        for decl in body.split(";"):
            if ":" in decl:
                name, value = decl.split(":", 1)
                decls[name.strip()] = value.strip()
        rules.append((selectors, decls))
    return rules


def _chip_rules(css: str) -> list[tuple[str, dict[str, str]]]:
    return [
        (sel, decls)
        for selectors, decls in _rules(css)
        for sel in selectors
        if any(sel == base or sel.startswith(base + ".") for base in CHIP_SELECTORS)
    ]


def _fill_alpha(value: str) -> float | None:
    """Pigment alpha of a fill, or None for a non-wash fill; 'selection' is a wash."""
    if value in ("@selection", "transparent", "none"):
        return 0.0
    wash = re.fullmatch(r"alpha\(@[\w-]+,\s*(\d*\.?\d+)\)", value)
    if wash:
        return float(wash.group(1))
    rgba = re.fullmatch(r"rgba\(\d+,\s*\d+,\s*\d+,\s*(\d*\.?\d+)\)", value)
    if rgba:
        return float(rgba.group(1))
    return None


def _assert_washes(css: str, expected: set[str]) -> None:
    chips = _chip_rules(css)
    assert expected <= {sel for sel, _ in chips}, f"missing chip rules: {expected}"
    for sel, decls in chips:
        for prop in ("background", "background-color"):
            if prop not in decls:
                continue
            alpha = _fill_alpha(decls[prop])
            assert alpha is not None, f"{sel}: {prop}: {decls[prop]} is a solid fill"
            assert alpha <= WASH_ALPHA_MAX, f"{sel}: {prop} alpha {alpha} > {WASH_ALPHA_MAX}"


def test_light_waybar_count_badge_and_tile_are_washes(light: dict[str, str]) -> None:
    _assert_washes(waybar_content(light), {"#custom-updates"})


def test_light_waybar_badge_has_neutral_clay_fill_and_accent_text(light: dict[str, str]) -> None:
    css = waybar_content(light)
    assert f"@define-color selection {light['selection']};" in css
    badge = dict(_chip_rules(css))["#custom-updates"]
    assert badge["background"] == "@selection"
    assert badge["color"] == "@accent"
    assert contrast(light["accent"], light["selection"]) >= TEXT_MIN


def test_light_waybar_only_the_critical_state_uses_the_error_wash(light: dict[str, str]) -> None:
    chips = dict(_chip_rules(waybar_content(light)))
    critical = chips["#custom-updates.critical"]
    assert critical["color"] == "@error"
    alpha = _fill_alpha(critical["background"])
    assert alpha is not None and 0 < alpha <= WASH_ALPHA_MAX
    wash_over_paper = mix(light["error"], light["bg"], 1 - alpha)
    assert contrast(light["error"], wash_over_paper) >= TEXT_MIN
    for sel, decls in chips.items():
        if sel != "#custom-updates.critical":
            assert "@error" not in decls.get("background", "")


def test_live_ml4w_override_washes_the_saturated_badge_and_tile() -> None:
    css = LIVE_OVERRIDE.read_text(encoding="utf-8")
    _assert_washes(css, {"#custom-updates.red", "#custom-updates.yellow"})
    chips = dict(_chip_rules(css))
    # The ML4W launcher keeps its glyph: blanking it loses the launcher (recolour is a T11 item).
    assert "#custom-ml4w-welcome" not in css
    # Only generated colour variables, never a hand-copied hex.
    values = [value for _, decls in _rules(css) for value in decls.values()]
    assert not [v for v in values if re.search(r"#[0-9a-fA-F]{3,8}\b", v)]


def test_light_waybar_artifact_carries_the_chip_rules(light: dict[str, str]) -> None:
    artifact = (THEMES / "waybar-light.css").read_text(encoding="utf-8")
    assert artifact == waybar_content(light)
    _assert_washes(artifact, {"#custom-updates"})


def test_dark_waybar_has_no_chip_rules(dark: dict[str, str]) -> None:
    assert "custom-updates" not in waybar_content(dark)
    assert "custom-ml4w-welcome" not in waybar_content(dark)
    assert "@selection" not in waybar_content(dark)


# ── Hyprland ────────────────────────────────────────────────────────────────

BORDER = re.compile(r"col\.active_border = (.+)")


def test_light_active_border_is_one_solid_accent(light: dict[str, str]) -> None:
    for text in (hypr_content(light), (THEMES / "hyprland-light.conf").read_text("utf-8")):
        match = BORDER.search(text)
        assert match, text
        assert match.group(1).strip() == f"rgba({light['accent'][1:]}ff)"
        assert "deg" not in match.group(1)
        assert f"col.inactive_border = rgba({light['border'][1:]}d9)" in text


def test_light_inactive_border_is_unchanged(light: dict[str, str]) -> None:
    assert "col.inactive_border = rgba(908379d9)" in hypr_content(light)


def test_dark_active_border_keeps_its_gradient(dark: dict[str, str]) -> None:
    border = BORDER.search(hypr_content(dark))
    assert border
    assert (
        border.group(1).strip() == f"rgba({dark['text'][1:]}ff) rgba({dark['muted'][1:]}ff) 45deg"
    )


# ── Gentle Shell / Pi ───────────────────────────────────────────────────────


def _assert_light_fill(name: str, fill: str, texts: list[str]) -> None:
    lightness = hex_to_oklch(fill)[0]
    assert lightness >= DARKEST_FILL_L, f"{name} {fill} has OKLab L {lightness:.3f}"
    for text in texts:
        assert contrast(text, fill) >= TEXT_MIN, f"{name}: {text} on {fill}"


def _flatten(light: dict[str, str], value: str) -> str:
    """Resolve an 8-digit hex over the Light paper; leave 6-digit hex alone."""
    if len(value) == 9:
        return mix("#" + value[1:7], light["bg"], 1 - int(value[7:], 16) / 255)
    return value


def test_pi_light_tool_and_message_blocks_have_no_dark_fill(light: dict[str, str]) -> None:
    theme = json.loads(pi_theme_content(light))
    colors = theme["colors"]
    for key in (
        "selectedBg",
        "userMessageBg",
        "customMessageBg",
        "toolPendingBg",
        "toolSuccessBg",
        "toolErrorBg",
    ):
        _assert_light_fill(key, colors[key], [light["text"], light["muted"]])


def test_pi_light_blocks_take_a_pigment_rule_not_a_pigment_fill(light: dict[str, str]) -> None:
    colors = json.loads(pi_theme_content(light))["colors"]
    # Pigment lives on the left rule and the title, ink on the body.
    assert colors["borderAccent"] == "lucuma"
    assert colors["toolTitle"] == "lucuma"
    assert colors["toolOutput"] == ""
    assert colors["customMessageLabel"] == "lucuma"


def test_gentle_shell_light_theme_surfaces_have_no_dark_fill(light: dict[str, str]) -> None:
    theme = json.loads(gentle_shell_theme_content(light, "light"))["colors"]
    for key in ("background", "canvas", "chrome", "surface", "raised", "popover", "hover"):
        _assert_light_fill(key, theme[key], [theme["foreground"], theme["muted"]])
    # A row selection is a translucent pigment wash over paper, never a dark block.
    selected = _flatten(light, theme["selected"])
    _assert_light_fill("selected", selected, [theme["foreground"]])
    # The accent button is a control, not a block: it only has to keep its label readable.
    assert contrast(theme["solid_foreground"], theme["solid"]) >= TEXT_MIN


def test_gentle_shell_light_tokens_have_no_dark_fill(light: dict[str, str]) -> None:
    tokens = gentle_shell_tokens(light, "light")
    for key in ("canvas", "background", "chrome", "surface", "raised", "user", "selected", "hover"):
        _assert_light_fill(key, tokens[key], [tokens["text"], tokens["muted"]])


def test_tracked_light_shell_and_pi_artifacts_match_the_renderers(light: dict[str, str]) -> None:
    pi = ROOT / "DreamcoderPi/.pi/agent/themes/dreamcoder-light.json"
    shell = ROOT / "DreamcoderHerdr/.config/herdr-app/themes/dreamcoder-shell-light.json"
    assert pi.read_text("utf-8") == pi_theme_content(light)
    assert shell.read_text("utf-8") == gentle_shell_theme_content(light, "light")
