import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

from dreamcoder_theme.settings import theme_paths
from dreamcoder_theme.writers import write_if_changed

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts" / "sync-dreamcoder-theme.py"

REQUIRED_PI_TOKENS = {
    "accent",
    "border",
    "borderAccent",
    "borderMuted",
    "success",
    "error",
    "warning",
    "muted",
    "dim",
    "text",
    "thinkingText",
    "selectedBg",
    "userMessageBg",
    "userMessageText",
    "customMessageBg",
    "customMessageText",
    "customMessageLabel",
    "toolPendingBg",
    "toolSuccessBg",
    "toolErrorBg",
    "toolTitle",
    "toolOutput",
    "mdHeading",
    "mdLink",
    "mdLinkUrl",
    "mdCode",
    "mdCodeBlock",
    "mdCodeBlockBorder",
    "mdQuote",
    "mdQuoteBorder",
    "mdHr",
    "mdListBullet",
    "toolDiffAdded",
    "toolDiffRemoved",
    "toolDiffContext",
    "syntaxComment",
    "syntaxKeyword",
    "syntaxFunction",
    "syntaxVariable",
    "syntaxString",
    "syntaxNumber",
    "syntaxType",
    "syntaxOperator",
    "syntaxPunctuation",
    "thinkingOff",
    "thinkingMinimal",
    "thinkingLow",
    "thinkingMedium",
    "thinkingHigh",
    "thinkingXhigh",
    "bashMode",
}


def run_sync(tmp: Path, mode: str = "dark") -> subprocess.CompletedProcess[str]:
    pi_agent = tmp / "pi-agent"
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(tmp / "home"),
            "XDG_CACHE_HOME": str(tmp / "cache"),
            "BAT_CACHE_PATH": str(tmp / "cache/bat"),
            "BAT_THEME_DIR": str(tmp / "config/bat/themes"),
            "BAT_CONFIG_PATH": os.devnull,
            "GHOSTTY_CONFIG": str(tmp / "ghostty/config"),
            "TMUX_THEME": str(tmp / "config/tmux/theme.conf"),
            "ZELLIJ_CONFIG": str(tmp / "config/zellij/config.kdl"),
            "WARP_SETTINGS": str(tmp / "warp/settings.toml"),
            "ORCA_DATA_PATH": str(tmp / "config/orca/orca-data.json"),
            "ORCA_STATE_DB_PATH": str(tmp / "config/orca/profile-state.db"),
            "DREAMCODER_HYPR_COLORS_LUA": str(tmp / "config/hypr/colors.lua"),
            "DREAMCODER_HYPR_COLORS_CONF": str(tmp / "config/hypr/colors.conf"),
            "DREAMCODER_WAYBAR_MATUGEN": str(tmp / "config/waybar/colors.css"),
            "DREAMCODER_ROFI_MATUGEN": str(tmp / "config/rofi/colors.rasi"),
            **{
                f"DREAMCODER_{target}_{kind}": str(tmp / "toolkits" / target / kind)
                for target in ("GTK3", "GTK4", "QT6CT")
                for kind in ("CONFIG", "CANONICAL", "STATE")
            },
            "GENTLE_SHELL_HOME": str(tmp / "gentle-agent"),
            "PI_CODING_AGENT_DIR": str(pi_agent),
            "PI_THEME": str(pi_agent / "themes/dreamcoder.json"),
            "PI_SETTINGS": str(pi_agent / "settings.json"),
            "DREAMCODER_THEME_MODE": mode,
            "DREAMCODER_ADAPTIVE": "0",
            "DREAMCODER_WRITE_REPO": "0",
            "XDG_CONFIG_HOME": str(tmp / "config"),
            "XDG_DATA_HOME": str(tmp / "data"),
            "PI_AGENT_DIR": str(pi_agent),
            "KITTY_COLORS": str(tmp / "kitty" / "colors.conf"),
            "KITTY_CONFIG": str(tmp / "kitty" / "kitty.conf"),
            "KITTY_DREAMCODER_UI": str(tmp / "kitty" / "dreamcoder-ui.conf"),
            "GHOSTTY_THEME": str(tmp / "ghostty" / "themes" / "dreamcoder"),
            "STARSHIP_CONFIG": str(tmp / "starship.toml"),
            "DREAMCODER_LAZYGIT_THEME": str(tmp / "lazygit" / "config.yml"),
            "WARP_THEME": str(tmp / "warp" / "Dreamcoder.yaml"),
            "OPENCODE_THEME": str(tmp / "opencode" / "themes" / "dreamcoder.json"),
            "OPENCODE_TUI": str(tmp / "opencode" / "tui.json"),
            "CODEX_THEME": str(tmp / "codex" / "themes" / "Dreamcoder.tmTheme"),
            "CODEX_CONFIG": str(tmp / "codex" / "config.toml"),
            # Repo-root active theme files: without these, sync_active_targets
            # writes the DreamcoderThemes/* files in the repository itself.
            "DREAMCODER_ZSH_SYNTAX_THEME": str(tmp / "themes" / "zsh-syntax.zsh"),
            "DREAMCODER_LS_COLORS_THEME": str(tmp / "themes" / "ls-colors.sh"),
            "DREAMCODER_BAT_THEME": str(tmp / "themes" / "bat.sh"),
            "DREAMCODER_DELTA_THEME": str(tmp / "themes" / "delta.gitconfig"),
            "DREAMCODER_FZF_THEME": str(tmp / "themes" / "fzf.sh"),
            "DREAMCODER_BTOP_THEME": str(tmp / "themes" / "btop.theme"),
            "DREAMCODER_DUNST_THEME": str(tmp / "themes" / "dunst.conf"),
            "DREAMCODER_FIREFOX_THEME": str(tmp / "themes" / "firefox.css"),
            "DREAMCODER_OBSIDIAN_THEME": str(tmp / "themes" / "obsidian.css"),
            "DREAMCODER_CAVA_THEME": str(tmp / "themes" / "cava.config"),
            "DREAMCODER_HYPRLAND_THEME": str(tmp / "themes" / "hyprland.conf"),
            "DREAMCODER_WAYBAR_THEME": str(tmp / "themes" / "waybar.css"),
            "DREAMCODER_ROFI_THEME": str(tmp / "themes" / "rofi.rasi"),
            "DREAMCODER_NVIM_THEME": str(tmp / "nvim" / "colors" / "dreamcoder.lua"),
            "PYTHONPATH": str(ROOT / "src"),
        }
    )
    return subprocess.run(
        [sys.executable, str(SYNC)],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


@pytest.mark.parametrize("state", ["missing", "dangling", "matching"])
def test_stable_theme_replacement_is_idempotent(tmp_path, state):
    destination = tmp_path / "themes/dreamcoder.json"
    source = tmp_path / "variant.json"
    destination.parent.mkdir()
    if state == "matching":
        source.write_text("canonical\n")
    if state != "missing":
        destination.symlink_to(source)
    assert write_if_changed(destination, "canonical\n", replace_symlink=True)
    assert not destination.is_symlink()
    assert destination.read_text() == "canonical\n"
    assert not write_if_changed(destination, "canonical\n", replace_symlink=True)
    if state == "matching":
        assert source.read_text() == "canonical\n"
    else:
        assert not source.exists()


@pytest.mark.parametrize("linked", [False, True])
def test_agent_home_precedence(monkeypatch, tmp_path, linked):
    monkeypatch.setenv("HOME", str(tmp_path))
    for key in (
        "PI_AGENT_DIR",
        "PI_CODING_AGENT_DIR",
        "PI_THEME",
        "PI_SETTINGS",
        "GENTLE_SHELL_HOME",
    ):
        monkeypatch.delenv(key, raising=False)
    paths = theme_paths()
    assert paths.pi_theme == tmp_path / ".pi/agent/themes/dreamcoder.json"
    assert paths.gentle_shell_theme == tmp_path / ".gentle-shell/agent/themes/dreamcoder.json"
    monkeypatch.setenv("PI_AGENT_DIR", str(tmp_path / "legacy"))
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("GENTLE_SHELL_HOME", str(tmp_path / ("runtime" if linked else "isolated")))
    paths = theme_paths()
    assert paths.pi_settings == tmp_path / "runtime/settings.json"
    assert paths.gentle_shell_settings is not None
    assert paths.gentle_shell_settings.parent == tmp_path / ("runtime" if linked else "isolated")
    monkeypatch.setenv("PI_THEME", str(tmp_path / "custom/theme.json"))
    monkeypatch.setenv("PI_SETTINGS", str(tmp_path / "custom/settings.json"))
    assert theme_paths().pi_theme == tmp_path / "custom/theme.json"
    assert theme_paths().pi_settings == tmp_path / "custom/settings.json"


class PiThemeGenerationTest(unittest.TestCase):
    def test_both_modes_update_both_homes_without_writing_through_legacy_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "repository-variant.json"
            source.write_text("do not mutate\n")
            for home in (tmp / "pi-agent", tmp / "gentle-agent"):
                (home / "themes").mkdir(parents=True)
                (home / "themes/dreamcoder.json").symlink_to(source)
                (home / "settings.json").write_text(
                    json.dumps({"theme": "light", "packages": ["keep"]})
                )
            for mode in ("light", "dark"):
                result = run_sync(tmp, mode)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                themes = []
                for home in (tmp / "pi-agent", tmp / "gentle-agent"):
                    path = home / "themes/dreamcoder.json"
                    self.assertFalse(path.is_symlink())
                    themes.append(json.loads(path.read_text()))
                    self.assertEqual(
                        json.loads((home / "settings.json").read_text()),
                        {"theme": "dreamcoder-light/dreamcoder-dark", "packages": ["keep"]},
                    )
                    variants = [
                        json.loads((home / "themes" / f"dreamcoder-{name}.json").read_text())
                        for name in ("dark", "light")
                    ]
                    self.assertEqual(
                        [variant["name"] for variant in variants],
                        ["dreamcoder-dark", "dreamcoder-light"],
                    )
                    self.assertEqual(
                        [variant["appearance"] for variant in variants], ["dark", "light"]
                    )
                    self.assertEqual(
                        {themes[-1]["name"], *(variant["name"] for variant in variants)},
                        {"dreamcoder", "dreamcoder-dark", "dreamcoder-light"},
                    )
                self.assertEqual(themes[0], themes[1])
                self.assertEqual(
                    themes[0]["vars"]["lucuma"],
                    "#A5B4FC" if mode == "dark" else "#824f16",
                )
                self.assertEqual(source.read_text(), "do not mutate\n")

    def test_generates_global_pi_theme_with_all_required_tokens(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            result = run_sync(tmp, "dark")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            theme_path = tmp / "pi-agent" / "themes" / "dreamcoder.json"
            self.assertTrue(theme_path.exists(), "PI theme was not generated")
            theme = json.loads(theme_path.read_text())

            self.assertEqual(theme["name"], "dreamcoder")
            self.assertEqual(set(theme["colors"].keys()), REQUIRED_PI_TOKENS)
            self.assertEqual(theme["colors"]["accent"], "lucuma")
            self.assertEqual(theme["vars"]["lucuma"], "#A5B4FC")

    def test_tool_card_backgrounds_stay_on_the_neutral_surface_ladder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            result = run_sync(tmp, "dark")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            theme = json.loads((tmp / "pi-agent" / "themes" / "dreamcoder.json").read_text())

            # Gentle Shell paints floating cards and the prompt frame with
            # toolSuccessBg/toolPendingBg, so those roles must stay neutral
            # instead of borrowing the success hue.
            self.assertEqual(theme["colors"]["toolSuccessBg"], "#0D0D0F")
            self.assertEqual(theme["colors"]["toolPendingBg"], "#0B0B0B")

    def test_opencode_preserves_terminal_transparent_background(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            result = run_sync(tmp, "dark")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            theme_path = tmp / "opencode" / "themes" / "dreamcoder.json"
            theme = json.loads(theme_path.read_text())["theme"]

            self.assertEqual(theme["background"], "none")
            self.assertEqual(theme["backgroundPanel"], "none")
            self.assertEqual(theme["backgroundElement"], "#0B0B0B")
            self.assertEqual(theme["primary"], "#A5B4FC")
            self.assertEqual(theme["secondary"], "#D4B5FD")

    def test_selects_dreamcoder_theme_without_overwriting_existing_pi_settings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            settings_path = tmp / "pi-agent" / "settings.json"
            settings_path.parent.mkdir(parents=True)
            settings_path.write_text(
                json.dumps(
                    {
                        "defaultProvider": "openai-codex",
                        "packages": ["gentle-pi"],
                        "theme": "light",
                    },
                    indent=2,
                )
                + "\n"
            )

            result = run_sync(tmp, "light")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            settings = json.loads(settings_path.read_text())
            self.assertEqual(settings["theme"], "dreamcoder-light/dreamcoder-dark")
            self.assertEqual(settings["defaultProvider"], "openai-codex")
            self.assertEqual(settings["packages"], ["gentle-pi"])


if __name__ == "__main__":
    unittest.main()
