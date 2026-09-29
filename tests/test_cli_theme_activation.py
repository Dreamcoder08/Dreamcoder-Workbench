"""CLI theme activation + transaction/rollback (Phase 5, tasks 5.2/5.3/5.5/5.7).

Covers R7/R4 scenarios: ``theme apply`` persists the Light/Dark base, ``night``
is no longer an accepted choice, a failing gate changes nothing and exits
non-zero, and an injected
post-commit write/reload failure restores file bytes, symlink targets, and
prior settings. Tests drive ``control.main`` directly (no subprocess) with an
isolated temp config home; the system/reload adapter is mocked.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest import mock

import pytest

from dreamcoder_theme import cli_handlers, control
from dreamcoder_theme.settings import theme_paths
from dreamcoder_theme.settings_store import settings_get

# Map of env vars whose default path lives inside the repository, so the
# activation transaction writes only under the isolated temp config home.
_REPO_PATH_ENV: tuple[tuple[str, str], ...] = (
    ("DREAMCODER_NVIM_THEME", "nvim/colors/dreamcoder.lua"),
    ("DREAMCODER_ZSH_SYNTAX_THEME", "themes/zsh-syntax.zsh"),
    ("DREAMCODER_LS_COLORS_THEME", "themes/ls-colors.sh"),
    ("DREAMCODER_BAT_THEME", "themes/bat.sh"),
    ("DREAMCODER_DELTA_THEME", "themes/delta.gitconfig"),
    ("DREAMCODER_FZF_THEME", "themes/fzf.sh"),
    ("DREAMCODER_BTOP_THEME", "themes/btop.theme"),
    ("DREAMCODER_LAZYGIT_THEME", "lazygit/repo/config.yml"),
    ("DREAMCODER_DUNST_THEME", "themes/dunst.conf"),
    ("DREAMCODER_FIREFOX_THEME", "themes/firefox.css"),
    ("DREAMCODER_OBSIDIAN_THEME", "themes/obsidian.css"),
    ("DREAMCODER_CAVA_THEME", "themes/cava.config"),
    ("DREAMCODER_HYPRLAND_THEME", "themes/hyprland.conf"),
    ("DREAMCODER_WAYBAR_THEME", "themes/waybar.css"),
    ("DREAMCODER_ROFI_THEME", "themes/rofi.rasi"),
)


# Every other individually-named override env var settings.theme_paths()
# recognizes. Its config_home-relative fallback for these IS covered by the
# XDG_CONFIG_HOME/HOME monkeypatch below, but only if the ambient shell
# hasn't independently exported the override itself — os.environ.get(name,
# fallback) always prefers a set override over an isolated fallback. A
# fish/zsh profile commonly exports STARSHIP_CONFIG, which previously let
# this fixture's activation calls write straight through the real
# ~/.config/starship.toml symlink into the checked-in repo file on any
# machine where that export exists. Clear all of them defensively so this
# isolation doesn't depend on what happens to be unset in the developer's
# shell.
_UNSCOPED_OVERRIDE_ENV: tuple[str, ...] = (
    "KITTY_COLORS",
    "KITTY_CONFIG",
    "KITTY_DREAMCODER_UI",
    "GHOSTTY_THEME",
    "GHOSTTY_CONFIG",
    "STARSHIP_CONFIG",
    "TMUX_THEME",
    "ZELLIJ_CONFIG",
    "WARP_THEME",
    "WARP_SETTINGS",
    "OPENCODE_THEME",
    "OPENCODE_TUI",
    "CODEX_THEME",
    "CODEX_CONFIG",
    "CODEX_HOME",
    "PI_THEME",
    "PI_SETTINGS",
    "PI_AGENT_DIR",
    "DREAMCODER_TOKENS",
    "BAT_THEME_DIR",
)


@pytest.fixture
def theme_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate the full activation surface under a temp config home."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / ".local" / "share"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / ".cache"))
    monkeypatch.setenv("DREAMCODER_WRITE_REPO", "0")
    monkeypatch.setenv("DREAMCODER_CLEAN_OPENCODE_THEMES", "0")
    monkeypatch.delenv("DREAMCODER_THEME_MODE", raising=False)
    monkeypatch.delenv("DREAMCODER_SYNC_DONE", raising=False)
    monkeypatch.delenv("DREAMCODER_WALLPAPER", raising=False)
    for env_name in _UNSCOPED_OVERRIDE_ENV:
        monkeypatch.delenv(env_name, raising=False)
    cfg = tmp_path / ".config"
    for env_name, rel in _REPO_PATH_ENV:
        monkeypatch.setenv(env_name, str(cfg / rel))
    return tmp_path


def _run(
    choice: str, capsys: pytest.CaptureFixture[str], *, reload_failure: bool = False
) -> tuple[int, dict]:
    """Run one ``theme apply {choice} --json`` through the control path."""
    with mock.patch("dreamcoder_theme.cli_handlers.run_reload_adapter") as adapter:
        if reload_failure:
            adapter.side_effect = RuntimeError("injected reload failure")
        else:
            adapter.return_value = None
        rc = control.main(["theme", "apply", choice, "--json"])
    return rc, json.loads(capsys.readouterr().out)


def _tree_state(root: Path) -> dict[str, str]:
    """Capture the exact byte/link state of every file under a tree."""
    state: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            state[path.relative_to(root).as_posix()] = f"link:{os.readlink(path)}"
        elif path.is_file():
            state[path.relative_to(root).as_posix()] = f"file:{path.read_bytes().decode()}"
    return state


# ---------------------------------------------------------------------------
# R7: Light/Dark activation
# ---------------------------------------------------------------------------


def test_dark_activation_persists_base(theme_home: Path, capsys) -> None:
    rc, payload = _run("dark", capsys)
    assert rc == 0
    assert settings_get("terminal.default_mode") == "dark"
    assert payload["requested"] == "dark"
    assert payload["effective_base"] == "dark"
    assert "effective_profile" not in payload
    assert payload["coverage"] == "33/33"
    assert payload["rollback_state"] == "none"
    assert payload["changed"]["kitty"] is True
    assert theme_paths().kitty.exists()


def test_light_from_dark_regenerates_all_active(theme_home: Path, capsys) -> None:
    _run("dark", capsys)
    dark_kitty = theme_paths().kitty.read_bytes()
    rc, payload = _run("light", capsys)
    assert rc == 0
    assert settings_get("terminal.default_mode") == "light"
    assert payload["coverage"] == "33/33"
    assert payload["rollback_state"] == "none"
    assert theme_paths().kitty.read_bytes() != dark_kitty  # active outputs regenerated


def test_night_choice_is_rejected(theme_home: Path, capsys) -> None:
    before = _tree_state(theme_home)
    with pytest.raises(SystemExit) as exc:
        control.main(["theme", "apply", "night", "--json"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
    assert _tree_state(theme_home) == before


def test_activation_ignores_and_preserves_legacy_render_profile(theme_home: Path, capsys) -> None:
    """A settings file from the Night era still activates cleanly."""
    settings_file = theme_home / ".config/dreamcoder/settings.json"
    settings_file.parent.mkdir(parents=True)
    settings_file.write_text(json.dumps({"theme": {"render_profile": "night"}}))
    rc, payload = _run("light", capsys)
    assert rc == 0
    assert payload["effective_base"] == "light"
    assert settings_get("terminal.default_mode") == "light"
    assert settings_get("theme.render_profile") == "night"  # preserved, never read


# ---------------------------------------------------------------------------
# R4/R7: a failing gate changes no settings/output and exits non-zero
# ---------------------------------------------------------------------------


def test_failing_gate_changes_no_settings_or_output_and_exits_nonzero(
    theme_home: Path, capsys
) -> None:
    before = _tree_state(theme_home)
    with mock.patch("dreamcoder_theme.sync.validate_palette", return_value=["forced gate failure"]):
        rc, payload = _run("dark", capsys)
    assert rc != 0
    assert payload["rollback_state"] == "rejected"
    assert payload["errors"] == ["forced gate failure"]
    assert _tree_state(theme_home) == before  # zero writes
    assert settings_get("terminal.default_mode") is None  # nothing persisted


# ---------------------------------------------------------------------------
# R4/§8: injected post-commit failures restore bytes, symlink targets, settings
# ---------------------------------------------------------------------------


def test_post_commit_reload_failure_restores_bytes_symlinks_and_settings(
    theme_home: Path, capsys
) -> None:
    # Seed prior state: light with a matugen bridge symlink exactly as
    # the shell adapter would leave it (colors.css -> colors-light.css).
    _run("light", capsys)
    paths = theme_paths()
    real_content = paths.waybar_matugen.read_bytes()
    paths.waybar_matugen.unlink()
    bridge = paths.waybar_matugen.parent / "colors-light.css"
    bridge.write_bytes(real_content)
    os.symlink("colors-light.css", paths.waybar_matugen)
    before = _tree_state(theme_home)

    rc, payload = _run("dark", capsys, reload_failure=True)
    assert rc != 0
    assert payload["rollback_state"] == "restored"
    assert _tree_state(theme_home) == before
    assert os.readlink(paths.waybar_matugen) == "colors-light.css"
    assert bridge.read_text() == real_content.decode()
    assert settings_get("terminal.default_mode") == "light"


def test_post_commit_write_failure_restores_bytes_symlinks_and_settings(
    theme_home: Path, capsys
) -> None:
    _run("light", capsys)
    before = _tree_state(theme_home)

    calls = {"n": 0}

    def failing_writer(path: Path, content: str) -> bool:
        calls["n"] += 1
        if calls["n"] == 3:
            raise OSError("injected write failure")
        return True

    with mock.patch("dreamcoder_theme.sync.write_if_changed", side_effect=failing_writer):
        rc, payload = _run("dark", capsys)
    assert rc != 0
    assert payload["rollback_state"] == "restored"
    assert _tree_state(theme_home) == before
    assert settings_get("terminal.default_mode") == "light"


# ---------------------------------------------------------------------------
# R7/5.7: end-to-end settings transitions, no partial cross-target state
# ---------------------------------------------------------------------------


def test_dark_light_dark_end_to_end_transitions(theme_home: Path, capsys) -> None:
    transitions: list[str] = []
    for choice in ("dark", "light", "dark"):
        rc, payload = _run(choice, capsys)
        assert rc == 0
        assert payload["coverage"] == "33/33"
        assert payload["rollback_state"] == "none"
        transitions.append(settings_get("terminal.default_mode"))
    assert transitions == ["dark", "light", "dark"]


# ---------------------------------------------------------------------------
# Lazygit: token-driven active file + live symlink surface (R4/§8)
# ---------------------------------------------------------------------------


def test_dark_activation_writes_lazygit_active_and_leaves_live_link_to_python(
    theme_home: Path, capsys
) -> None:
    """Dark activation writes the repo active config; the live symlink stays
    owned by the shell adapter (apply-theme-mode.sh) and is only snapshotted.
    """
    paths = theme_paths()
    live = theme_home / ".config/lazygit"
    live.mkdir(parents=True)
    (live / "config.dark.yml").write_text("# seeded variant\n")
    os.symlink("config.dark.yml", live / "config.yml")

    rc, payload = _run("dark", capsys)
    assert rc == 0
    assert payload["coverage"] == "33/33"
    assert payload["changed"]["lazygit"] is True
    assert paths.lazygit.exists()  # repo active file was written
    assert os.readlink(live / "config.yml") == "config.dark.yml"  # untouched


def test_reload_failure_restores_lazygit_active_and_live_symlink(theme_home: Path, capsys) -> None:
    """A post-commit reload failure restores the Lazygit active file bytes and
    the seeded live symlink target exactly (rollback of the adapter surface).
    """
    _run("light", capsys)
    paths = theme_paths()
    active_before = paths.lazygit.read_bytes()
    live = theme_home / ".config/lazygit"
    live.mkdir(parents=True, exist_ok=True)
    (live / "config.dark.yml").write_text("# seeded variant\n")
    (live / "config.yml").unlink(missing_ok=True)
    os.symlink("config.dark.yml", live / "config.yml")
    before = _tree_state(theme_home)

    rc, payload = _run("dark", capsys, reload_failure=True)
    assert rc != 0
    assert payload["rollback_state"] == "restored"
    assert _tree_state(theme_home) == before
    assert paths.lazygit.read_bytes() == active_before
    assert os.readlink(live / "config.yml") == "config.dark.yml"
    assert settings_get("terminal.default_mode") == "light"


# ---------------------------------------------------------------------------
# R7: generic settings interface stays available
# ---------------------------------------------------------------------------


def test_transaction_snapshots_herdr_config_path_override(
    theme_home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    override = theme_home / "custom/herdr.toml"
    monkeypatch.setenv("HERDR_CONFIG_PATH", str(override))

    assert override in cli_handlers._mutable_paths(theme_paths())


def test_reload_failure_restores_herdr_override_selector(
    theme_home: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    override = theme_home / "custom/herdr.toml"
    override.parent.mkdir(parents=True)
    old_target = theme_home / "old.toml"
    new_target = theme_home / "new.toml"
    old_target.write_text("# old\n")
    new_target.write_text("# new\n")
    os.symlink(old_target, override)
    monkeypatch.setenv("HERDR_CONFIG_PATH", str(override))

    def fail_after_switch(_base: str) -> None:
        override.unlink()
        os.symlink(new_target, override)
        raise RuntimeError("injected Herdr reload failure")

    with mock.patch(
        "dreamcoder_theme.cli_handlers.run_reload_adapter", side_effect=fail_after_switch
    ):
        rc = control.main(["theme", "apply", "light", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["rollback_state"] == "restored"
    assert Path(os.readlink(override)) == old_target


def test_generic_settings_interface_keeps_working(theme_home: Path, capsys) -> None:
    assert control.main(["settings", "set", "motion.active", "fluid", "--json"]) == 0
    capsys.readouterr()
    assert settings_get("motion.active") == "fluid"
    assert control.main(["settings", "get", "motion.active", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["value"] == "fluid"
