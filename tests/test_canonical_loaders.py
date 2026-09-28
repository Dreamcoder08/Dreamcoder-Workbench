"""Canonical loader tests (task 2.5): thresholds come from tokens, never code.

`load_guardrails()` reads the canonical guardrail floors from `tokens.json`
and fails closed when a required key is missing — no policy literals are permitted on the runtime path
(ADR-002, R2/R3).
"""

import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import apca_lc
from dreamcoder_theme.palette import (
    load_guardrails,
    validate_palette,
)

ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = ROOT / "DreamcoderThemes" / "dreamcoder"

# Every threshold key the dual gate resolves; all must be present in the
# canonical file, proving no APCA/WCAG threshold is a code literal.
REQUIRED_THRESHOLD_KEYS = (
    "minimum_text_contrast",
    "preferred_main_text_contrast",
    "minimum_terminal_ansi_contrast",
    "minimum_terminal_selection_contrast",
    "minimum_apca_body",
    "minimum_apca_body_dark",
    "minimum_apca_quiet",
    "minimum_apca_ui",
    "minimum_apca_ui_dark",
    "minimum_apca_on_accent",
    "minimum_apca_heading_light",
    "minimum_apca_heading_dark",
)


def _tokens() -> dict:
    return json.loads((THEME_ROOT / "tokens.json").read_text())


def _write_tokens(tmp_path: Path, tokens: dict) -> Path:
    out = tmp_path / "tokens.json"
    out.write_text(json.dumps(tokens), encoding="utf-8")
    return out


def test_load_guardrails_returns_canonical_numeric_floors():
    g = load_guardrails(THEME_ROOT / "tokens.json")
    assert g["minimum_apca_quiet"] == 44
    assert g["minimum_apca_body"] == 75
    assert g["minimum_apca_body_dark"] == 50
    assert g["minimum_apca_ui_dark"] == 28
    assert g["minimum_apca_heading_light"] == 60
    assert g["minimum_apca_heading_dark"] == 45
    assert g["minimum_apca_on_accent"] == 60


def test_every_gate_threshold_key_exists_in_loaded_guardrails():
    g = load_guardrails(THEME_ROOT / "tokens.json")
    for key in REQUIRED_THRESHOLD_KEYS:
        assert key in g, f"threshold key {key} not loaded from canonical tokens"


def test_load_guardrails_fails_when_required_key_missing(tmp_path):
    tokens = _tokens()
    del tokens["guardrails"]["minimum_apca_quiet"]
    with pytest.raises(ValueError, match="minimum_apca_quiet"):
        load_guardrails(_write_tokens(tmp_path, tokens))


def test_load_guardrails_fails_on_missing_file(tmp_path):
    with pytest.raises(ValueError, match="tokens file not found"):
        load_guardrails(tmp_path / "missing.json")


def test_gate_uses_loaded_threshold_not_a_literal(tmp_path):
    """Raise the quiet floor in the canonical file: the gate must follow it."""
    tokens = _tokens()
    tokens["guardrails"]["minimum_apca_quiet"] = 55
    g = load_guardrails(_write_tokens(tmp_path, tokens))
    pal = dict(tokens["modes"]["dark"])
    errors = validate_palette(pal, g, mode="dark")
    quiet_errors = [e for e in errors if "class=quiet" in e and "minimum_apca_quiet" in e]
    assert quiet_errors, "quiet floor change was not picked up from loaded tokens"
    assert "=55" in quiet_errors[0]
    assert abs(apca_lc(pal["subtle"], pal["bg"])) < 55
