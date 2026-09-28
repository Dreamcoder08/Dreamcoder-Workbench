"""Deterministic candidate validation tests (task 2.6).

The dual gate (ADR-002) is exercised against the deterministic candidates:
Light, Dark, and design-system Dusk (adaptive disabled for the gate —
candidates are built directly from the canonical token modes, never through
``adaptive_palette``). All must pass both the WCAG 2.2 and APCA floors. Per-class at-floor passes and
just-below-floor failures are asserted for Heading (Lc 60 light / 45 dark),
Body (75 light / 50 dark), Quiet (44), UI (60 light / 28 dark), and On-accent
(60), using the mode-aware floor keys.
"""

import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import apca_lc, contrast
from dreamcoder_theme.palette import (
    load_guardrails,
    validate_palette,
)

ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = ROOT / "DreamcoderThemes" / "dreamcoder"


def _tokens() -> dict:
    return json.loads((THEME_ROOT / "tokens.json").read_text())


def _guardrails() -> dict[str, float]:
    return load_guardrails(THEME_ROOT / "tokens.json")


def _nearest_gray(
    bg: str, target_apca: float, *, direction: str, require_wcag: float = 0.0
) -> tuple[str, float, float]:
    """Deterministically find the gray whose |APCA| is nearest ``target_apca``
    on the given background, above or below the floor (optionally also meeting
    a WCAG floor). Returns (hex, |apca|, wcag)."""
    best: tuple[float, str, float, float] | None = None
    for level in range(256):
        gray = f"#{level:02x}{level:02x}{level:02x}"
        lc = abs(apca_lc(gray, bg))
        wcag = contrast(gray, bg)
        if direction == "above":
            if lc < target_apca or wcag < require_wcag:
                continue
        elif lc >= target_apca:
            continue
        distance = abs(lc - target_apca)
        if best is None or distance < best[0]:
            best = (distance, gray, lc, wcag)
    if best is None:
        pytest.fail(f"no gray found {direction} APCA {target_apca} on {bg}")
    return best[1], best[2], best[3]


# ---------------------------------------------------------------------------
# Deterministic candidates
# ---------------------------------------------------------------------------


def test_candidates_all_pass_the_dual_gate():
    tokens = _tokens()
    g = _guardrails()
    for mode in ("light", "dark", "dusk"):
        errors = validate_palette(dict(tokens["modes"][mode]), g, mode=mode)
        assert errors == [], f"{mode} gate failures: {errors}"


def test_candidates_use_canonical_palettes_not_adaptive_output():
    """Adaptive is disabled for the gate: canonical mode bytes are the input."""
    tokens = _tokens()
    for mode in ("light", "dark", "dusk"):
        assert tokens["modes"][mode]["details"] in ("darker", "lighter")
    assert tokens["modes"]["dusk"]["name"] == "Dreamcoder Dusk"


# ---------------------------------------------------------------------------
# Per-class at-floor / just-below-floor boundaries
# ---------------------------------------------------------------------------


def _palette_for(mode: str) -> dict[str, str]:
    return dict(_tokens()["modes"][mode])


def _assert_class_floor(mode: str, fg_key: str, floor_key: str, pair_bg: str | None = None):
    """At-floor gray passes the class; just-below gray fails with the key."""
    g = _guardrails()
    floor = g[floor_key]
    pal = _palette_for(mode)
    bg = pal[pair_bg] if pair_bg else pal["bg"]

    above, above_lc, above_wcag = _nearest_gray(bg, floor, direction="above", require_wcag=4.5)
    assert above_lc >= floor and above_wcag >= 4.5
    pal_above = dict(pal)
    pal_above[fg_key] = above
    errors = validate_palette(pal_above, g, mode=mode)
    assert not [e for e in errors if f"{fg_key}/{pair_bg or 'bg'}" in e], (
        f"{mode}.{fg_key} at-floor {above} (Lc {above_lc:.1f} >= {floor}) should pass"
    )

    below, below_lc, _ = _nearest_gray(bg, floor, direction="below")
    assert below_lc < floor
    pal_below = dict(pal)
    pal_below[fg_key] = below
    errors = validate_palette(pal_below, g, mode=mode)
    apca_errors = [e for e in errors if "APCA fail" in e and f"pair={fg_key}/" in e]
    assert apca_errors, (
        f"{mode}.{fg_key} just-below {below} (Lc {below_lc:.1f} < {floor}) must block"
    )
    assert floor_key in apca_errors[0]
    assert f"={floor}" in apca_errors[0]


def test_heading_floor_light_60():
    _assert_class_floor("light", "text_heading", "minimum_apca_heading_light")


def test_heading_floor_dark_45():
    _assert_class_floor("dark", "text_heading", "minimum_apca_heading_dark")


def test_body_floor_light_75():
    _assert_class_floor("light", "success", "minimum_apca_body")


def test_body_floor_dark_50():
    _assert_class_floor("dark", "error", "minimum_apca_body_dark")


def test_quiet_floor_44_light():
    _assert_class_floor("light", "disabled", "minimum_apca_quiet")


def test_quiet_floor_44_dark():
    _assert_class_floor("dark", "subtle", "minimum_apca_quiet")


def test_ui_floor_light_60():
    _assert_class_floor("light", "border_ui", "minimum_apca_ui")


def test_ui_floor_dark_28():
    _assert_class_floor("dark", "border_ui", "minimum_apca_ui_dark")


def test_on_accent_floor_60_dark():
    _assert_class_floor("dark", "on_accent", "minimum_apca_on_accent", pair_bg="accent")


def test_on_accent_floor_60_light():
    _assert_class_floor("light", "on_accent", "minimum_apca_on_accent", pair_bg="accent")
