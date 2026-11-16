"""Active-mode mirrors are generated, not tracked (odd/tasks/active-mirrors-untracked.md).

Switching Light/Dark must leave ``git status`` clean. Every repository file whose
content is fully determined by tokens + the active mode is gitignored and
untracked (S2); the sync's repo pass writes each of them, including the
stow-routed ones that used to reach the repository only through a live symlink
(S3); hand-maintained configs select a mode-independent alias (S4); and
``DREAMCODER_WRITE_LIVE=0`` runs a repo-only sync that never touches ``$HOME``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

from dreamcoder_theme import settings, sync
from dreamcoder_theme.cli_handlers import _mutable_paths
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.settings import (
    active_mode_state_path,
    read_active_mode,
    theme_paths,
    write_active_mode,
    write_live_enabled,
)
from dreamcoder_theme.sync import write_live_zellij_theme
from dreamcoder_theme.writers import update_ghostty_theme, update_zellij_config

ROOT = Path(__file__).resolve().parents[1]

# Every active mirror the repo pass generates for the current mode. Exact
# paths only: the -dark/-light variants next to them stay tracked.
ACTIVE_MIRRORS = (
    ".opencode/themes/dreamcoder.json",
    "DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme",
    "DreamcoderCodexApp/Dreamcoder.codex-theme.json",
    "DreamcoderCodexCLI/Dreamcoder.tmTheme",
    "DreamcoderGhostty/.config/ghostty/themes/dreamcoder",
    "DreamcoderKitty/.config/kitty/colors-dreamcoder.conf",
    "DreamcoderKitty/.config/kitty/dreamcoder-ui.conf",
    "DreamcoderLazygit/.config/lazygit/config.yml",
    "DreamcoderPi/.pi/agent/themes/dreamcoder.json",
    "DreamcoderShell/.config/starship.toml",
    "DreamcoderThemes/bat-dreamcoder.sh",
    "DreamcoderThemes/btop-dreamcoder.theme",
    "DreamcoderThemes/cava-dreamcoder.config",
    "DreamcoderThemes/delta-dreamcoder.gitconfig",
    "DreamcoderThemes/dunst-dreamcoder.conf",
    "DreamcoderThemes/firefox-dreamcoder.css",
    "DreamcoderThemes/fzf-dreamcoder.sh",
    "DreamcoderThemes/hyprland.conf",
    "DreamcoderThemes/ls-colors-dreamcoder.sh",
    "DreamcoderThemes/obsidian-dreamcoder.css",
    "DreamcoderThemes/rofi.rasi",
    "DreamcoderThemes/waybar.css",
    "DreamcoderThemes/zsh-syntax-highlighting-dreamcoder.zsh",
    "DreamcoderThemes/dreamcoder/hyprland.conf",
    "DreamcoderThemes/dreamcoder/rofi.rasi",
    "DreamcoderThemes/dreamcoder/waybar.css",
    "DreamcoderTmux/.config/tmux/tmux-dreamcoder.conf",
    "DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder.yaml",
    "DreamcoderZellij/.config/zellij/themes/dreamcoder.kdl",
)

# Mode variants and hand-maintained selectors that must stay tracked.
TRACKED_NEIGHBOURS = (
    "DreamcoderGhostty/.config/ghostty/config",
    "DreamcoderGhostty/.config/ghostty/themes/dreamcoder-dark",
    "DreamcoderGhostty/.config/ghostty/themes/dreamcoder-light",
    "DreamcoderKitty/.config/kitty/colors-dreamcoder-dark.conf",
    "DreamcoderKitty/.config/kitty/colors-dreamcoder-light.conf",
    "DreamcoderShell/.config/starship-dark.toml",
    "DreamcoderShell/.config/starship-light.toml",
    "DreamcoderThemes/dreamcoder/hyprland-dark.conf",
    "DreamcoderThemes/dreamcoder/waybar-light.css",
    "DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder-Dark.yaml",
    "DreamcoderZellij/.config/zellij/config.kdl",
    "DreamcoderZellij/.config/zellij/dreamcoder-dark.kdl",
    "DreamcoderZellij/.config/zellij/dreamcoder-light.kdl",
    "DreamcoderFastfetch/.config/dreamcoder/settings.json",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False
    )


requires_git = pytest.mark.skipif(
    shutil.which("git") is None or not (ROOT / ".git").exists(),
    reason="needs a git checkout",
)


# ---------------------------------------------------------------------------
# S2: pure mirrors are ignored and untracked; variants stay tracked
# ---------------------------------------------------------------------------


@requires_git
@pytest.mark.parametrize("rel_path", ACTIVE_MIRRORS)
def test_active_mirror_is_gitignored(rel_path: str) -> None:
    result = _git("check-ignore", "--no-index", "-q", rel_path)
    assert result.returncode == 0, f"{rel_path} must be matched by .gitignore"


@requires_git
def test_active_mirrors_are_not_tracked() -> None:
    tracked = _git("ls-files", "--", *ACTIVE_MIRRORS).stdout.split()
    assert tracked == [], f"generated active mirrors still tracked: {tracked}"


@requires_git
@pytest.mark.parametrize("rel_path", TRACKED_NEIGHBOURS)
def test_variants_and_selectors_are_not_ignored(rel_path: str) -> None:
    result = _git("check-ignore", "--no-index", "-q", rel_path)
    assert result.returncode == 1, f"{rel_path} must stay tracked, not ignored"


# ---------------------------------------------------------------------------
# S4: hand-maintained selectors are mode-independent
# ---------------------------------------------------------------------------


def test_tracked_ghostty_config_selects_the_stable_alias() -> None:
    config = (ROOT / "DreamcoderGhostty/.config/ghostty/config").read_text()
    assert re.findall(r"^theme\s*=\s*(\S+)\s*$", config, re.MULTILINE) == ["dreamcoder"]


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_ghostty_selector_is_the_same_alias_in_both_modes(tmp_path: Path, mode: str) -> None:
    path = tmp_path / "config"
    path.write_text("font-size = 12\ntheme = dreamcoder-dark\n")
    assert update_ghostty_theme(path, mode) is True
    assert path.read_text() == "font-size = 12\ntheme = dreamcoder\n"
    assert update_ghostty_theme(path, mode) is False


def test_tracked_zellij_config_selects_the_stable_theme() -> None:
    config = (ROOT / "DreamcoderZellij/.config/zellij/config.kdl").read_text()
    assert re.findall(r'^\s*theme\s+"([^"]+)"\s*$', config, re.MULTILINE) == ["dreamcoder"]


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_zellij_selector_is_the_same_name_in_both_modes(tmp_path: Path, mode: str) -> None:
    path = tmp_path / "config.kdl"
    path.write_text('pane_frames false\ntheme "dreamcoder-light"\n')
    assert update_zellij_config(path, mode) is True
    assert path.read_text() == 'pane_frames false\ntheme "dreamcoder"\n'
    assert update_zellij_config(path, mode) is False


def test_generated_zellij_theme_defines_the_stable_name() -> None:
    variants = {mode: dict(palette) for mode, palette in VARIANTS.items()}
    content = sync.render_coverage_plan(theme_paths(), variants["light"], "light", variants)[
        "zellij"
    ]
    assert re.search(r"^themes \{\n    dreamcoder \{$", content, re.MULTILINE)


# ---------------------------------------------------------------------------
# S4: the activated mode lives in untracked state, not the tracked settings
# ---------------------------------------------------------------------------


@pytest.fixture
def state_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / ".local/state"))
    return tmp_path


def test_active_mode_state_lives_under_xdg_state_home(state_home: Path) -> None:
    assert active_mode_state_path() == state_home / ".local/state/dreamcoder/theme-mode"


def test_active_mode_round_trips_through_state_without_touching_settings(
    state_home: Path,
) -> None:
    settings = state_home / ".config/dreamcoder/settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({"terminal": {"default_mode": "light"}}))
    before = settings.read_bytes()

    write_active_mode("dark")

    assert read_active_mode() == "dark"
    assert active_mode_state_path().read_text() == "dark\n"
    assert settings.read_bytes() == before


def test_active_mode_falls_back_to_legacy_settings(state_home: Path) -> None:
    settings = state_home / ".config/dreamcoder/settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(json.dumps({"terminal": {"default_mode": "dark"}}))
    assert read_active_mode() == "dark"


def test_active_mode_ignores_invalid_state_and_falls_back(state_home: Path) -> None:
    active_mode_state_path().parent.mkdir(parents=True)
    active_mode_state_path().write_text("neon\n")
    assert read_active_mode() is None


def test_activation_snapshots_the_active_mode_state(state_home: Path) -> None:
    assert active_mode_state_path() in _mutable_paths(theme_paths())


# ---------------------------------------------------------------------------
# DREAMCODER_WRITE_LIVE: repo-only sync contract
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"), [(None, True), ("1", True), ("0", False), ("yes", True)]
)
def test_write_live_enabled_reads_the_environment(
    monkeypatch: pytest.MonkeyPatch, value: str | None, expected: bool
) -> None:
    if value is None:
        monkeypatch.delenv("DREAMCODER_WRITE_LIVE", raising=False)
    else:
        monkeypatch.setenv("DREAMCODER_WRITE_LIVE", value)
    assert write_live_enabled() is expected


def _main_calls(monkeypatch: pytest.MonkeyPatch, *, live: str | None, repo: str | None):
    for name, value in (("DREAMCODER_WRITE_LIVE", live), ("DREAMCODER_WRITE_REPO", repo)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    calls: list[str] = []
    prepared = mock.Mock(mode="light", active={}, variants={})

    def record(name: str, result):
        def _call(*_a, **_k):
            calls.append(name)
            return result

        return _call

    monkeypatch.setattr(sync.subprocess, "run", record("generate_tokens", None))
    monkeypatch.setattr(sync, "theme_paths", record("theme_paths", mock.Mock()))
    monkeypatch.setattr(sync, "theme_mode", lambda: "light")
    monkeypatch.setattr(sync, "prepare", lambda _base: prepared)
    monkeypatch.setattr(sync, "sync_active_targets", record("live", {}))
    monkeypatch.setattr(sync, "sync_bat_theme_variants", record("live_bat_variants", []))
    monkeypatch.setattr(sync, "ensure_bat_cache", record("bat_cache", None))
    monkeypatch.setattr(sync, "sync_orca_theme", record("orca", "ok"))
    monkeypatch.setattr(sync, "sync_repo_snippets", record("repo", [True]))
    monkeypatch.setattr(
        sync, "valid_starship", lambda path: calls.append(f"starship:{path}") or True
    )
    monkeypatch.setattr(sync, "print_summary", record("summary", None))
    sync.main([])
    return calls


def test_default_sync_keeps_writing_live_and_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _main_calls(monkeypatch, live=None, repo=None)
    for step in ("live", "live_bat_variants", "repo", "bat_cache", "orca"):
        assert step in calls


def test_write_repo_zero_still_skips_repo_outputs(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _main_calls(monkeypatch, live=None, repo="0")
    assert "repo" not in calls
    assert "live" in calls


def test_write_live_zero_runs_a_repo_only_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _main_calls(monkeypatch, live="0", repo=None)
    assert "repo" in calls
    for step in ("live", "live_bat_variants", "bat_cache", "orca"):
        assert step not in calls
    assert f"starship:{ROOT / 'DreamcoderShell/.config/starship.toml'}" in calls


def test_write_live_and_repo_both_zero_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as exc:
        _main_calls(monkeypatch, live="0", repo="0")
    assert "nothing to write" in str(exc.value)


def test_sync_help_documents_write_live(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    with pytest.raises(SystemExit):
        sync.main(["--help"])
    out = " ".join(capsys.readouterr().out.split())
    assert "DREAMCODER_WRITE_LIVE=0" in out


# ---------------------------------------------------------------------------
# S3 + S5 contract: a repo-only sync on a fresh copy produces every mirror
# and writes nothing under $HOME
# ---------------------------------------------------------------------------


@requires_git
def test_repo_only_sync_generates_every_active_mirror_without_touching_home(
    tmp_path: Path,
) -> None:
    clone = tmp_path / "clone"
    listed = _git("ls-files", "-z").stdout.split("\0")
    for rel in filter(None, listed):
        source = ROOT / rel
        if not source.is_file() or rel in ACTIVE_MIRRORS:
            continue
        target = clone / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=True)
    for rel in ACTIVE_MIRRORS:
        (clone / rel).unlink(missing_ok=True)

    home = tmp_path / "home"
    home.mkdir()
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("DREAMCODER_", "XDG_", "KITTY_", "GHOSTTY_", "PI_", "CODEX_"))
    }
    env.update(
        HOME=str(home),
        XDG_CONFIG_HOME=str(home / ".config"),
        XDG_DATA_HOME=str(home / ".local/share"),
        XDG_CACHE_HOME=str(home / ".cache"),
        XDG_STATE_HOME=str(home / ".local/state"),
        PYTHONPATH=str(clone / "src"),
        DREAMCODER_WRITE_LIVE="0",
        DREAMCODER_THEME_MODE="light",
        DREAMCODER_ADAPTIVE="0",
    )
    result = subprocess.run(
        [sys.executable, "-m", "dreamcoder_theme.sync"],
        cwd=clone,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    missing = [rel for rel in ACTIVE_MIRRORS if not (clone / rel).is_file()]
    assert missing == []
    assert not (clone / "DreamcoderKitty/.config/kitty/colors-dreamcoder.conf").is_symlink()
    written = sorted(p.relative_to(home).as_posix() for p in home.rglob("*"))
    assert written == [], f"repo-only sync wrote under $HOME: {written}"


# ---------------------------------------------------------------------------
# S3: stow-routed mirrors get a repo write with the live renderer's bytes
# ---------------------------------------------------------------------------

_STOW_ROUTED = (
    ("DreamcoderShell/.config/starship.toml", sync.starship_content),
    ("DreamcoderGhostty/.config/ghostty/themes/dreamcoder", sync.ghostty_content),
    ("DreamcoderTmux/.config/tmux/tmux-dreamcoder.conf", sync.tmux_content),
    ("DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder.yaml", sync.warp_content),
    ("DreamcoderKitty/.config/kitty/colors-dreamcoder.conf", sync.kitty_content),
)


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_repo_pass_writes_stow_routed_mirrors_for_the_active_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync, "VARIANT_REGISTRY", [])
    variants = {name: dict(palette) for name, palette in VARIANTS.items()}

    sync.sync_repo_snippets(variants, variants[mode])

    for rel_path, renderer in _STOW_ROUTED:
        written = (tmp_path / rel_path).read_text()
        assert written.rstrip("\n") == renderer(variants[mode]).rstrip("\n"), rel_path
    zellij = tmp_path / "DreamcoderZellij/.config/zellij/themes/dreamcoder.kdl"
    assert zellij.read_text() == sync.zellij_content(variants[mode], "dreamcoder")


def test_kitty_colors_symlink_becomes_a_file_without_corrupting_its_sibling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync, "VARIANT_REGISTRY", [])
    kitty_dir = tmp_path / "DreamcoderKitty/.config/kitty"
    kitty_dir.mkdir(parents=True)
    light = kitty_dir / "colors-dreamcoder-light.conf"
    light.write_text("light sibling\n")
    active = kitty_dir / "colors-dreamcoder.conf"
    active.symlink_to("colors-dreamcoder-light.conf")
    variants = {name: dict(palette) for name, palette in VARIANTS.items()}

    sync.sync_repo_snippets(variants, variants["dark"])

    assert not active.is_symlink()
    assert active.read_text().rstrip("\n") == sync.kitty_content(variants["dark"]).rstrip("\n")
    assert light.read_text() == "light sibling\n"


def test_live_zellij_theme_is_skipped_when_zellij_is_not_installed(tmp_path: Path) -> None:
    """Without a Zellij config, a live sync must not create themes/ (a later stow would conflict)."""
    config = tmp_path / ".config/zellij/config.kdl"
    assert write_live_zellij_theme(config, VARIANTS["light"]) is False
    assert not (tmp_path / ".config/zellij").exists()


def test_live_zellij_theme_is_written_next_to_an_existing_config(tmp_path: Path) -> None:
    config = tmp_path / ".config/zellij/config.kdl"
    config.parent.mkdir(parents=True)
    config.write_text('theme "dreamcoder"\n')
    assert write_live_zellij_theme(config, VARIANTS["light"]) is True
    assert (config.parent / "themes/dreamcoder.kdl").is_file()


def test_corrupt_mode_state_falls_back_to_the_legacy_setting(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    state = settings.active_mode_state_path()
    state.parent.mkdir(parents=True)
    state.write_text("purple\n")
    monkeypatch.setattr("dreamcoder_theme.settings_store.settings_get", lambda key: "light")
    assert settings.read_active_mode() == "light"
