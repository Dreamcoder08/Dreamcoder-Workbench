import json
import re
import unittest
from pathlib import Path

from dreamcoder_theme.renderers_ghostty_warp import ghostty_content
from dreamcoder_theme.renderers_kitty import kitty_ui_content

ROOT = Path(__file__).resolve().parents[1]
KITTY = ROOT / "DreamcoderKitty" / ".config" / "kitty"
GHOSTTY = ROOT / "DreamcoderGhostty" / ".config" / "ghostty" / "themes"


def parse_kitty(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, *rest = line.split()
        if rest:
            values[key] = rest[0]
    return values


def parse_ghostty(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("palette ="):
            _, value = line.split("=", 1)
            index, color = value.strip().split("=", 1)
            values[f"color{index}"] = color.strip()
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


class TerminalParityTest(unittest.TestCase):
    def test_kitty_and_ghostty_share_core_color_contract(self):
        mapping = {
            "foreground": "foreground",
            "background": "background",
            "selection_foreground": "selection-foreground",
            "selection_background": "selection-background",
            "cursor": "cursor-color",
            "cursor_text_color": "cursor-text",
        }
        for mode in ("light", "dark"):
            with self.subTest(mode=mode):
                kitty = parse_kitty(KITTY / f"colors-dreamcoder-{mode}.conf")
                ghostty = parse_ghostty(GHOSTTY / f"dreamcoder-{mode}")
                for kitty_key, ghostty_key in mapping.items():
                    self.assertEqual(kitty[kitty_key], ghostty[ghostty_key])
                for index in range(16):
                    self.assertEqual(kitty[f"color{index}"], ghostty[f"color{index}"])

    def test_rendered_terminal_opacity_and_blur_contract(self):
        variants = json.loads((ROOT / "DreamcoderThemes/dreamcoder/tokens.json").read_text())[
            "modes"
        ]
        for mode, opacity, kitty_blur, ghostty_blur in (
            ("dark", "1.0", "24", "true"),
            ("light", "0.96", "0", "false"),
        ):
            with self.subTest(mode=mode):
                kitty = dict(
                    line.split(maxsplit=1)
                    for line in kitty_ui_content(variants[mode]).splitlines()
                    if line.strip() and not line.startswith("#")
                )
                ghostty = ghostty_content(variants[mode])
                self.assertEqual(kitty["background_opacity"], opacity)
                self.assertEqual(kitty["background_blur"], kitty_blur)
                self.assertIn(f"background-opacity = {opacity}\n", ghostty)
                self.assertIn(f"background-blur = {ghostty_blur}\n", ghostty)
                if mode == "dark":
                    self.assertIn("background = #000000\n", ghostty)

    def test_kitty_light_readability_has_no_low_opacity_fallback(self):
        config = KITTY / "kitty.conf"
        opacities: list[float] = []
        dynamic_yes: list[str] = []
        for line in config.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("background_opacity"):
                match = re.search(r"background_opacity\s+([0-9.]+)", stripped)
                if match:
                    opacities.append(float(match.group(1)))
            if stripped == "dynamic_background_opacity yes":
                dynamic_yes.append(stripped)

        self.assertTrue(opacities, "kitty.conf must declare an explicit opacity fallback")
        self.assertGreaterEqual(min(opacities), 0.9)
        self.assertEqual(dynamic_yes, [])


if __name__ == "__main__":
    unittest.main()
