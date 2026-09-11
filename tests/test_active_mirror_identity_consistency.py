"""Regression coverage for cross-target Dark/Light identity consistency.

refresh-dreamcoder-dark-contrast's verify-report.md documented a real,
recurring defect: DreamcoderShell/.config/starship.toml silently reverted to the
Light identity while every other active mirror target stayed correctly on Dark.
Nothing in the suite caught it — pytest and scripts/verify-theme-health.py both
passed while the checked-in file diverged from the rest of the repository.

These tests assert every checked-in active mirror renders byte-identical to
exactly one canonical mode variant, that all of them agree on the same mode, and
that the mode selectors (Ghostty, Zellij, Fastfetch) select that same mode. The
coverage is exhaustive over the mirrors the repository ships, so a partial mode
switch cannot pass unnoticed.

Antigravity's unsuffixed Dreamcoder.json is NOT part of that group: unlike the
others, sync.py pins its active write to the Dark palette always
(verify-theme-health.py's check_antigravity_files requires
button.background/foreground to resolve Dark's accent_2/on_accent regardless of
the live active mode), so it is covered by its own always-Dark test below
instead of the flexible group-consistency check.
"""

from __future__ import annotations

import json
import re
from functools import partial
from pathlib import Path

import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers import (
    bat_content,
    btop_content,
    cava_content,
    codex_tmtheme_content,
    delta_content,
    dunst_content,
    firefox_content,
    fzf_content,
    ghostty_content,
    hypr_content,
    kitty_content,
    kitty_ui_content,
    lazygit_content,
    ls_colors_content,
    obsidian_content,
    opencode_content,
    pi_theme_content,
    rofi_content,
    starship_content,
    tmux_content,
    waybar_content,
    zsh_syntax_content,
)
from dreamcoder_theme.renderers_antigravity import antigravity_content

ROOT = Path(__file__).resolve().parents[1]

# Every checked-in active mirror this repository ships for the active mode.
# codex_app's file is opencode-schema JSON (sync.py wires it to
# opencode_content), not the codex_tmtheme_content the renderer_registry
# module's "codex_app" entry claims — that registry/sync mismatch is
# pre-existing and out of scope here; this test follows sync.py, the renderer
# actually invoked by the theme sync.
_ACTIVE_MIRROR_TARGETS = (
    (
        ".opencode",
        ".opencode/themes/dreamcoder.json",
        partial(opencode_content, transparent_background=True),
    ),
    ("bat", "DreamcoderThemes/bat-dreamcoder.sh", bat_content),
    ("bat_theme", "DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme", codex_tmtheme_content),
    ("btop", "DreamcoderThemes/btop-dreamcoder.theme", btop_content),
    ("cava", "DreamcoderThemes/cava-dreamcoder.config", cava_content),
    ("codex_app", "DreamcoderCodexApp/Dreamcoder.codex-theme.json", opencode_content),
    ("codex_theme", "DreamcoderCodexCLI/Dreamcoder.tmTheme", codex_tmtheme_content),
    ("delta", "DreamcoderThemes/delta-dreamcoder.gitconfig", delta_content),
    ("dunst", "DreamcoderThemes/dunst-dreamcoder.conf", dunst_content),
    ("firefox", "DreamcoderThemes/firefox-dreamcoder.css", firefox_content),
    ("fzf", "DreamcoderThemes/fzf-dreamcoder.sh", fzf_content),
    ("ghostty_theme", "DreamcoderGhostty/.config/ghostty/themes/dreamcoder", ghostty_content),
    ("hyprland", "DreamcoderThemes/hyprland.conf", hypr_content),
    ("hyprland_repo", "DreamcoderThemes/dreamcoder/hyprland.conf", hypr_content),
    ("kitty", "DreamcoderKitty/.config/kitty/colors-dreamcoder.conf", kitty_content),
    ("kitty_ui", "DreamcoderKitty/.config/kitty/dreamcoder-ui.conf", kitty_ui_content),
    ("lazygit", "DreamcoderLazygit/.config/lazygit/config.yml", lazygit_content),
    ("ls_colors", "DreamcoderThemes/ls-colors-dreamcoder.sh", ls_colors_content),
    ("obsidian", "DreamcoderThemes/obsidian-dreamcoder.css", obsidian_content),
    ("pi_theme", "DreamcoderPi/.pi/agent/themes/dreamcoder.json", pi_theme_content),
    ("rofi", "DreamcoderThemes/rofi.rasi", rofi_content),
    ("rofi_repo", "DreamcoderThemes/dreamcoder/rofi.rasi", rofi_content),
    ("starship", "DreamcoderShell/.config/starship.toml", starship_content),
    ("tmux", "DreamcoderTmux/.config/tmux/tmux-dreamcoder.conf", tmux_content),
    ("waybar", "DreamcoderThemes/waybar.css", waybar_content),
    ("waybar_repo", "DreamcoderThemes/dreamcoder/waybar.css", waybar_content),
    ("zsh_syntax", "DreamcoderThemes/zsh-syntax-highlighting-dreamcoder.zsh", zsh_syntax_content),
)

# Ghostty keeps the legacy `dreamcoder` name for standard light.
_GHOSTTY_THEME_BY_MODE = {"dark": "dreamcoder-dark", "light": "dreamcoder"}


def _identity(content: str, renderer) -> str:
    content = content.rstrip("\n")
    if content == renderer(VARIANTS["dark"]).rstrip("\n"):
        return "dark"
    if content == renderer(VARIANTS["light"]).rstrip("\n"):
        return "light"
    return "unknown"


def _identities() -> dict[str, str]:
    return {
        name: _identity((ROOT / rel_path).read_text(encoding="utf-8"), renderer)
        for name, rel_path, renderer in _ACTIVE_MIRROR_TARGETS
    }


def _agreed_mode() -> str:
    identities = _identities()
    modes_seen = set(identities.values())
    assert modes_seen in ({"dark"}, {"light"}), (
        f"active mirror targets disagree on identity: {identities} — this is "
        f"exactly the defect class where one target (e.g. starship.toml) "
        f"silently reverts while the rest stay on the prior mode"
    )
    return next(iter(modes_seen))


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
    mode = _agreed_mode()
    assert mode in {"dark", "light"}


def test_mode_selectors_agree_with_active_mirrors() -> None:
    mode = _agreed_mode()

    ghostty = (ROOT / "DreamcoderGhostty/.config/ghostty/config").read_text(encoding="utf-8")
    expected_ghostty = _GHOSTTY_THEME_BY_MODE[mode]
    assert re.search(rf"^theme\s*=\s*{re.escape(expected_ghostty)}\s*$", ghostty, re.MULTILINE), (
        f"Ghostty config must select {expected_ghostty!r} for the active {mode} mode"
    )

    zellij = (ROOT / "DreamcoderZellij/.config/zellij/config.kdl").read_text(encoding="utf-8")
    assert re.search(rf'^theme\s+"dreamcoder-{mode}"', zellij, re.MULTILINE), (
        f"Zellij config must select 'dreamcoder-{mode}' for the active {mode} mode"
    )

    settings = json.loads(
        (ROOT / "DreamcoderFastfetch/.config/dreamcoder/settings.json").read_text(encoding="utf-8")
    )
    assert settings["terminal"]["default_mode"] == mode, (
        "Fastfetch settings default_mode must match the active mirror mode"
    )


def test_antigravity_active_file_is_always_pinned_dark() -> None:
    content = (ROOT / "DreamcoderAntigravity/Dreamcoder.json").read_text(encoding="utf-8")
    assert content.rstrip("\n") == antigravity_content(VARIANTS["dark"]).rstrip("\n"), (
        "DreamcoderAntigravity/Dreamcoder.json must always render the Dark "
        "palette regardless of the live active mode (verify-theme-health.py "
        "requires button.background/foreground to resolve Dark's "
        "accent_2/on_accent)"
    )
