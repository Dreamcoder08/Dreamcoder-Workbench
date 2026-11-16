"""The vendored Gentle Shell Desktop mods follow the canonical Dreamcoder palette."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dreamcoder_theme._math import contrast
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers_gentle_shell import (
    gentle_shell_theme_content,
    gentle_shell_tokens,
    gentle_tokens_js_content,
)

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "DreamcoderHerdr/.config/herdr-app"
TOKENS_FILES = sorted((APP / "mods").glob("gentle-*/tokens.js"))
# Upstream Gentleman pink: none may survive the recolour.
UPSTREAM_HEX = ("#f095c8", "#be1d7d", "#060407", "#fbf7f9")


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_layout_themes_are_generated_from_tokens(mode: str) -> None:
    shipped = (APP / f"themes/dreamcoder-shell-{mode}.json").read_text()
    assert shipped == gentle_shell_theme_content(VARIANTS[mode], mode)
    colors = json.loads(shipped)["colors"]
    assert colors["accent"] == VARIANTS[mode]["accent"].upper()
    assert colors["canvas"] == VARIANTS[mode]["bg"].upper()


def test_layout_selects_the_dreamcoder_shell_themes() -> None:
    layout = json.loads((APP / "layouts/gentle-shell.json").read_text())
    assert layout["theme"] == {"light": "dreamcoder-shell-light", "dark": "dreamcoder-shell-dark"}


def test_every_vendored_tokens_js_is_recoloured() -> None:
    assert len(TOKENS_FILES) == 10
    for path in TOKENS_FILES:
        text = path.read_text()
        assert gentle_tokens_js_content(text, VARIANTS["dark"], VARIANTS["light"]) == text, path
        for hex_value in UPSTREAM_HEX:
            assert hex_value not in text.lower(), (path, hex_value)


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_text_tokens_keep_aa_contrast(mode: str) -> None:
    t = gentle_shell_tokens(VARIANTS[mode], mode)
    for fg in ("text", "muted", "faint", "accent", "err", "warn", "ok", "info"):
        for bg in ("canvas", "chrome", "surface", "selected", "user"):
            assert contrast(t[fg], t[bg]) >= 4.5, (mode, fg, bg)
    assert contrast(t["onAccent"], t["accent"]) >= 4.5


def test_unknown_upstream_token_is_refused() -> None:
    source = 'const HEX = {\n  brandNew: "#123456",\n};\nconst HEX_LIGHT = {\n};\n'
    with pytest.raises(ValueError, match="brandNew"):
        gentle_tokens_js_content(source, VARIANTS["dark"], VARIANTS["light"])


def test_gentle_shell_keys_use_linux_modifiers() -> None:
    keys = json.loads((APP / "keys.json").read_text())["layout:gentle-shell"]
    assert keys["ctrl-shift-g"] == "mod.open:gentle-palette"
    assert keys["ctrl-shift-j"] == "gentle-status.toggle"
    assert not any(chord.startswith("cmd-") for chord in keys)


def _mods(node: dict) -> set[str]:
    found = set()
    for key in ("content",):
        content = node.get(key)
        if isinstance(content, dict) and "mod" in content:
            found.add(content["mod"])
    for item in node.get("floating", []):
        found |= _mods(item)
    for child in node.get("children", []):
        found |= _mods(child)
    return found


def test_gentle_shell_carries_the_former_dreamcoder_cockpit() -> None:
    assert not list((APP / "layouts").glob("dreamcoder*")), "dreamcoder layouts were folded in"
    layout = json.loads((APP / "layouts/gentle-shell.json").read_text())
    assert {"files", "prs", "flow", "dc-panels", "dc-status", "verify", "needs-you"} <= _mods(
        layout
    )


def test_no_key_targets_a_removed_layout_or_mod() -> None:
    keys = json.loads((APP / "keys.json").read_text())
    actions = [action for section in keys.values() for action in section.values()]
    assert not any("dc-tabs" in a or a.startswith("layout.switch:dreamcoder") for a in actions)
    assert keys["global"]["alt-c"] == "layout.switch:gentle-shell"
    assert keys["global"]["alt-p"] == "dc-panels.panel-prs"
    assert keys["global"]["alt-b"] == "dc-panels.panel-files"
