"""Regression coverage for cross-target Dark/Light identity consistency.

refresh-dreamcoder-dark-contrast's verify-report.md documented a real,
recurring defect: DreamcoderShell/.config/starship.toml silently reverted to
the Light identity while every other "active-and-repository" mirror target
stayed correctly on Dark. Nothing in the suite caught it — pytest and
scripts/verify-theme-health.py both passed while the checked-in file
diverged from the rest of the repository.

These tests assert every checked-in "active-and-repository" mirror renders
byte-identical to exactly one canonical mode variant, and that all of them
agree on the same mode. opencode's active target uses a different adapter
path (TransparentOpenCodeAdapter, no checked-in mode-suffixed repository
variant) and is intentionally not covered here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_antigravity import antigravity_content
from dreamcoder_theme.renderers_codex import codex_tmtheme_content
from dreamcoder_theme.renderers_opencode import opencode_content
from dreamcoder_theme.renderers_pi import pi_theme_content
from dreamcoder_theme.renderers_starship import starship_content

ROOT = Path(__file__).resolve().parents[1]

# codex_app's checked-in file is opencode-schema JSON (sync.py wires it to
# opencode_content), not the codex_tmtheme_content the renderer_registry
# module's "codex_app" entry claims — that registry/sync mismatch is
# pre-existing and out of scope here; this test follows sync.py, the
# renderer actually invoked by ./scripts/dreamcoder sync.
_ACTIVE_MIRROR_TARGETS = (
    ("starship", "DreamcoderShell/.config/starship.toml", starship_content),
    ("antigravity", "DreamcoderAntigravity/Dreamcoder.json", antigravity_content),
    ("pi_theme", "DreamcoderPi/.pi/agent/themes/dreamcoder.json", pi_theme_content),
    ("codex_app", "DreamcoderCodexApp/Dreamcoder.codex-theme.json", opencode_content),
    ("codex_theme", "DreamcoderCodexCLI/Dreamcoder.tmTheme", codex_tmtheme_content),
    ("bat_theme", "DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme", codex_tmtheme_content),
)


def _identity(content: str, renderer) -> str:
    content = content.rstrip("\n")
    if content == renderer(VARIANTS["dark"]).rstrip("\n"):
        return "dark"
    if content == renderer(VARIANTS["light"]).rstrip("\n"):
        return "light"
    return "unknown"


@pytest.mark.parametrize(("name", "rel_path", "renderer"), _ACTIVE_MIRROR_TARGETS)
def test_active_mirror_matches_exactly_one_canonical_mode(
    name: str, rel_path: str, renderer
) -> None:
    content = (ROOT / rel_path).read_text(encoding="utf-8")
    identity = _identity(content, renderer)
    assert identity != "unknown", (
        f"{rel_path} does not byte-match either the Dark or Light rendered "
        f"variant for consumer {name!r} — it has drifted from both canonical "
        f"identities"
    )


def test_active_mirrors_all_agree_on_the_same_mode() -> None:
    identities = {
        name: _identity((ROOT / rel_path).read_text(encoding="utf-8"), renderer)
        for name, rel_path, renderer in _ACTIVE_MIRROR_TARGETS
    }
    modes_seen = set(identities.values())
    assert modes_seen in ({"dark"}, {"light"}), (
        f"active mirror targets disagree on identity: {identities} — this is "
        f"exactly the defect class where one target (e.g. starship.toml) "
        f"silently reverts while the rest stay on the prior mode"
    )
