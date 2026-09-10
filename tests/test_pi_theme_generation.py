import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


class PiThemeGenerationTest(unittest.TestCase):
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

    def test_opencode_preserves_terminal_transparent_background(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            result = run_sync(tmp, "dark")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            theme_path = tmp / "opencode" / "themes" / "dreamcoder.json"
            theme = json.loads(theme_path.read_text())["theme"]

            self.assertEqual(theme["background"], "none")
            self.assertEqual(theme["backgroundPanel"], "#0D0D0F")
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
            self.assertEqual(settings["theme"], "dreamcoder")
            self.assertEqual(settings["defaultProvider"], "openai-codex")
            self.assertEqual(settings["packages"], ["gentle-pi"])


if __name__ == "__main__":
    unittest.main()
