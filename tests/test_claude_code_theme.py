"""Claude Code custom theme: diff bands follow the Dreamcoder palette."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import contrast
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers import claude_code_theme_content

ROOT = Path(__file__).resolve().parent.parent
REPO_THEMES = ROOT / "DreamcoderClaudeCode/.claude/themes"
DIFF_KEYS = (
    "diffAdded",
    "diffRemoved",
    "diffAddedDimmed",
    "diffRemovedDimmed",
    "diffAddedWord",
    "diffRemovedWord",
)


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_theme_uses_the_matching_base_and_every_diff_key(mode: str) -> None:
    theme = json.loads(claude_code_theme_content(VARIANTS[mode]))
    assert theme["name"] == "Dreamcoder"
    assert theme["base"] == mode
    assert set(theme["overrides"]) == set(DIFF_KEYS)


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_diff_text_stays_readable_and_bands_stay_visible(mode: str) -> None:
    palette = VARIANTS[mode]
    o = json.loads(claude_code_theme_content(palette))["overrides"]
    for key in DIFF_KEYS:
        assert contrast(palette["text"], o[key]) >= 7.0, key
    for kind in ("Added", "Removed"):
        line, word = o[f"diff{kind}"], o[f"diff{kind}Word"]
        assert contrast(line, palette["bg"]) >= 1.1, kind
        assert contrast(word, palette["bg"]) > contrast(line, palette["bg"]), kind
    assert o["diffAdded"] != o["diffRemoved"]


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_repo_variants_match_the_renderer(mode: str) -> None:
    shipped = (REPO_THEMES / f"dreamcoder-{mode}.json").read_text()
    assert shipped == claude_code_theme_content(VARIANTS[mode])
