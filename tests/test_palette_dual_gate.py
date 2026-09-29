"""Dual-gate tests for validate_palette (WCAG 2.2 + APCA, ADR-002).

Both metrics are independently blocking: a WCAG pass never waives an APCA
failure and an APCA pass never waives a WCAG failure. Thresholds are resolved
from the passed guardrails by key; diagnostics carry metric, mode/profile,
pair, measured value, and guardrail key/value.
"""

import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import apca_lc, contrast
from dreamcoder_theme.palette import validate_palette

ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = ROOT / "DreamcoderThemes" / "dreamcoder"


def _guardrails() -> dict[str, float]:
    tokens = json.loads((THEME_ROOT / "tokens.json").read_text())
    return {k: v for k, v in tokens["guardrails"].items() if isinstance(v, (int, float))}


def _clean_palette(mode: str) -> dict[str, str]:
    """Canonical mode palette with the known contrast debt neutralized so a
    test can inject exactly one failing pair without unrelated noise.

    Known debt pairs (Phase 0.3 register + corrected dual gate): dark
    ``subtle``/``disabled``/``border_ui`` below APCA floors, and light
    ``disabled`` below the WCAG 4.5 floor.
    """
    tokens = json.loads((THEME_ROOT / "tokens.json").read_text())
    pal = dict(tokens["modes"][mode])
    if mode == "dark":
        pal["subtle"] = "#A8B5C2"
        pal["disabled"] = "#A8B5C2"
        pal["border_ui"] = "#A8B5C2"
    else:
        pal["success"] = pal["text"]
        pal["disabled"] = pal["text"]
    return pal


def test_wcag_pass_apca_fail_is_blocking():
    """WCAG >= 4.5 but APCA below the dark body floor must still block."""
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#7b7b7b"  # WCAG 4.67 vs bg, APCA 32.2 < body_dark 50
    assert contrast(pal["bg"], pal["diagnostic"]) >= 4.5
    assert abs(apca_lc(pal["diagnostic"], pal["bg"])) < _guardrails()["minimum_apca_body_dark"]

    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert any("APCA fail" in e and "diagnostic/bg" in e for e in errors)
    assert not any("WCAG fail" in e and "diagnostic/bg" in e for e in errors)


def test_apca_pass_wcag_fail_is_blocking():
    """APCA above the floor but WCAG < 4.5 must still block."""
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#1b1b1b"  # APCA 57.1 (black soft clamp), WCAG 1.15
    assert abs(apca_lc(pal["diagnostic"], pal["bg"])) >= _guardrails()["minimum_apca_body_dark"]
    assert contrast(pal["bg"], pal["diagnostic"]) < 4.5

    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert any("WCAG fail" in e and "diagnostic/bg" in e for e in errors)
    assert not any("APCA fail" in e and "diagnostic/bg" in e for e in errors)


def test_light_wcag_pass_apca_fail_is_blocking():
    """Light body floor (75): a WCAG pass alone must not waive APCA."""
    pal = _clean_palette("light")
    pal["diagnostic"] = "#545454"  # WCAG 6.35, APCA 74.5 < body 75
    assert contrast(pal["bg"], pal["diagnostic"]) >= 4.5
    assert abs(apca_lc(pal["diagnostic"], pal["bg"])) < _guardrails()["minimum_apca_body"]

    errors = validate_palette(pal, _guardrails(), mode="light")

    assert any("APCA fail" in e and "diagnostic/bg" in e for e in errors)
    assert not any("WCAG fail" in e and "diagnostic/bg" in e for e in errors)


def test_both_metric_failures_accumulate():
    """A pair failing both metrics yields both diagnostics, not a short-circuit."""
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#4a4a4a"  # WCAG 2.23 and APCA 11.8 — both fail
    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert any("WCAG fail" in e and "diagnostic/bg" in e for e in errors)
    assert any("APCA fail" in e and "diagnostic/bg" in e for e in errors)


def test_diagnostic_carries_guardrail_key_and_value():
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#7b7b7b"
    errors = validate_palette(pal, _guardrails(), mode="dark")
    apca_errors = [e for e in errors if "APCA fail" in e and "diagnostic/bg" in e]
    assert len(apca_errors) == 1
    assert "minimum_apca_body_dark" in apca_errors[0]
    assert "=50" in apca_errors[0]
    assert "mode=dark" in apca_errors[0]


def test_missing_apca_guardrail_key_fails_closed():
    pal = _clean_palette("dark")
    guardrails = dict(_guardrails())
    del guardrails["minimum_apca_body_dark"]
    errors = validate_palette(pal, guardrails, mode="dark")
    assert any("missing guardrail key: minimum_apca_body_dark" in e for e in errors)


def test_mode_derives_from_palette_when_omitted():
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#7b7b7b"
    errors = validate_palette(pal, _guardrails())
    assert any("mode=dark" in e for e in errors if "APCA fail" in e)


def test_near_invisible_quiet_pair_fails_wcag_despite_apca_boost():
    """CRITICAL regression (R1): the APCA low-contrast boost must not let a
    visually indistinguishable pair pass the dual gate — the independent WCAG
    floor on the same declared pair must block it."""
    pal = _clean_palette("dark")
    pal["subtle"] = "#1b1b1b"  # WCAG 1.15 vs bg, but APCA 57.1 >= quiet 44 (boosted)
    assert contrast(pal["bg"], pal["subtle"]) < 4.5
    assert abs(apca_lc(pal["subtle"], pal["bg"])) >= _guardrails()["minimum_apca_quiet"]

    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert any("WCAG fail" in e and "subtle/bg" in e for e in errors)


def test_every_declared_pair_requires_both_metrics():
    """Every APCA-class pair (quiet included) must carry an independent WCAG
    floor — an APCA pass alone never waives WCAG (ADR-002)."""
    pal = _clean_palette("dark")
    pal["border_ui"] = "#1b1b1b"  # APCA 57.1 >= ui_dark 28, WCAG 1.15 < 4.5
    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert any("WCAG fail" in e and "border_ui/bg" in e for e in errors)
    assert not any("APCA fail" in e and "border_ui/bg" in e for e in errors)


def test_invalid_mode_is_rejected():
    pal = _clean_palette("dark")
    errors = validate_palette(pal, _guardrails(), mode="bogus")
    assert any("invalid mode: bogus" in e for e in errors)


def test_dusk_uses_light_floors():
    """Dusk is a design-system light-mode variant: it must use the light APCA
    floors, never the weaker dark floors (design class table)."""
    pal = _clean_palette("dark")
    pal["diagnostic"] = "#7b7b7b"  # APCA 32.2 < body 75 (light floor) and < body_dark 50
    errors = validate_palette(pal, _guardrails(), mode="dusk")
    apca_errors = [e for e in errors if "APCA fail" in e and "diagnostic/bg" in e]
    assert len(apca_errors) == 1
    assert "minimum_apca_body" in apca_errors[0]
    assert "minimum_apca_body_dark" not in apca_errors[0]


def test_missing_declared_pair_token_is_reported():
    pal = _clean_palette("dark")
    pal.pop("text_heading")
    errors = validate_palette(pal, _guardrails(), mode="dark")
    assert any("missing token: text_heading (declared heading pair)" in e for e in errors)


# -- Characterization: exact error list and order ---------------------------
# Frozen snapshot of the canonical dark palette so the golden list below stays
# independent of future token edits; it pins every validate_palette branch and
# the exact order in which errors are emitted.
_FROZEN_DARK = {
    "bg": "#000000",
    "bg_soft": "#0B0B0B",
    "surface0": "#0B0B0B",
    "surface1": "#0D0D0F",
    "surface2": "#1F1F1F",
    "surface3": "#2E2E2E",
    "text": "#E6E6E6",
    "text_heading": "#F5F5F5",
    "muted": "#C7C7C7",
    "subtle": "#A7A7A7",
    "comment": "#D0D0D0",
    "border": "#6B6B6B",
    "border_ui": "#767676",
    "border_hi": "#A7A7A7",
    "focus": "#3B82F6",
    "accent": "#A5B4FC",
    "accent_2": "#D4B5FD",
    "diagnostic": "#7DD3FC",
    "selection": "#3A3A3A",
    "details": "darker",
    "prompt_bg": "#000000",
    "prompt_surface0": "#0B0B0B",
    "prompt_surface1": "#0D0D0F",
    "prompt_surface2": "#1F1F1F",
    "prompt_text": "#E6E6E6",
    "prompt_muted": "#C7C7C7",
    "prompt_accent": "#A5B4FC",
    "prompt_accent_2": "#D4B5FD",
    "sage": "#34D399",
    "lavender": "#D4B5FD",
    "mauve": "#D8B4FE",
    "error": "#FB8585",
    "warning": "#FBBF24",
    "success": "#34D399",
    "info": "#7DD3FC",
    "selection_bg": "#3A3A3A",
    "selection_fg": "#E6E6E6",
    "on_surface": "#E6E6E6",
    "on_accent": "#000000",
    "on_error": "#000000",
    "on_focus": "#000000",
    "link": "#A5B4FC",
    "link_hover": "#D4B5FD",
    "disabled": "#A7A7A7",
    "hover": "#3A3A3A",
    "pressed": "#1F1F1F",
}


def test_error_list_and_order_are_stable_across_every_rule_family():
    pal = dict(_FROZEN_DARK)
    pal.pop("diagnostic")
    pal["text"] = "#8a8a8a"
    pal["selection_fg"] = pal["selection_bg"]
    pal["on_accent"] = pal["accent"]
    pal["surface1"] = pal["bg"]
    pal["subtle"] = pal["comment"]
    pal["accent_2"] = pal["accent"]
    guardrails = dict(_guardrails(), minimum_terminal_ansi_contrast=12.0)

    errors = validate_palette(pal, guardrails, mode="dark")

    ansi = "WCAG fail: mode=dark pair=ansi{}/bg measured={} guardrail=minimum_terminal_ansi_contrast=12.0"
    assert errors == [
        "missing token: diagnostic",
        "WCAG fail: mode=dark pair=text/bg measured=6.08 guardrail=preferred_main_text_contrast=7.0",
        "WCAG fail: mode=dark pair=selection_fg/selection_bg measured=1.00 "
        "guardrail=minimum_terminal_selection_contrast=7.0",
        "WCAG fail: mode=dark pair=on_accent/accent measured=1.00 guardrail=minimum_text_contrast=4.5",
        ansi.format(0, "4.82"),
        ansi.format(1, "8.80"),
        ansi.format(2, "10.92"),
        ansi.format(5, "11.88"),
        ansi.format(6, "11.83"),
        ansi.format(9, "8.15"),
        ansi.format(10, "9.76"),
        ansi.format(11, "11.06"),
        ansi.format(12, "11.13"),
        ansi.format(13, "10.59"),
        ansi.format(14, "5.64"),
        ansi.format(15, "6.08"),
        "APCA fail: mode=dark pair=text/bg class=body measured=39.6 "
        "guardrail=minimum_apca_body_dark=50",
        "missing token: diagnostic (declared body pair)",
        "APCA fail: mode=dark pair=on_accent/accent class=on-accent measured=16.0 "
        "guardrail=minimum_apca_on_accent=60",
        "WCAG fail: mode=dark pair=on_accent/accent measured=1.00 guardrail=minimum_text_contrast=4.5",
        "surface1 too close to bg",
        "comment and subtle must differ",
        "accent and accent_2 must differ",
    ]


def test_light_mode_without_surface3_is_reported_last():
    pal = _clean_palette("light")
    pal.pop("surface3")

    errors = validate_palette(pal, _guardrails())

    assert errors[-1] == "light mode missing surface3"


def test_missing_bg_fails_fast_with_key_error():
    pal = dict(_FROZEN_DARK)
    pal.pop("bg")

    with pytest.raises(KeyError, match="bg"):
        validate_palette(pal, _guardrails(), mode="dark")


def test_absent_foreground_pair_token_skips_its_wcag_check():
    pal = dict(_FROZEN_DARK)
    pal.pop("on_error")

    errors = validate_palette(pal, _guardrails(), mode="dark")

    assert not any("on_error/" in e for e in errors)


def test_missing_text_token_still_fails_through_the_ansi_derivation():
    """ANSI colors derive from ``text``, so a palette without it cannot be validated."""
    pal = dict(_FROZEN_DARK)
    pal.pop("text")

    with pytest.raises(KeyError, match="text"):
        validate_palette(pal, _guardrails(), mode="dark")
