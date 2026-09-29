"""Dual-gate tests for validate_palette (WCAG 2.2 + APCA, ADR-002).

Both metrics are independently blocking: a WCAG pass never waives an APCA
failure and an APCA pass never waives a WCAG failure. Thresholds are resolved
from the passed guardrails by key; diagnostics carry metric, mode/profile,
pair, measured value, and guardrail key/value.
"""

import json
from pathlib import Path

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
