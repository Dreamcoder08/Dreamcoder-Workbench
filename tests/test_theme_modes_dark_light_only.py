"""Dreamcoder has exactly two modes: Dark and Light (dusk was removed).

Spec: odd/tasks/dreamcoder-light-coherence.md, T13, S5 (decision D2).
An unknown mode such as the former ``dusk`` is rejected the same way any other
unknown mode is.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dreamcoder_theme import settings
from dreamcoder_theme.palette import load_guardrails, load_variants, validate_palette
from dreamcoder_theme.palette_tokens import VARIANTS

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
MODE_MESSAGE = "DREAMCODER_THEME_MODE must be 'dark' or 'light'"


def test_tokens_and_variants_expose_exactly_dark_and_light() -> None:
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))

    assert set(tokens["modes"]) == {"dark", "light"}
    assert set(VARIANTS) == {"dark", "light"}
    assert set(load_variants(VARIANTS, TOKENS)) == {"dark", "light"}
    assert "dusk_hours_default" not in tokens["guardrails"]
    assert tokens["name"] == "Dreamcoder Workbench"


@pytest.mark.parametrize("mode", ("dusk", "bogus"))
def test_unknown_theme_mode_env_is_rejected(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DREAMCODER_THEME_MODE", mode)

    with pytest.raises(SystemExit, match=MODE_MESSAGE):
        settings.theme_mode()


@pytest.mark.parametrize("mode", ("dusk", "bogus"))
def test_unknown_mode_fails_palette_validation(mode: str) -> None:
    errors = validate_palette(dict(VARIANTS["dark"]), load_guardrails(TOKENS), mode=mode)

    assert any(f"invalid mode: {mode}" in error for error in errors)
