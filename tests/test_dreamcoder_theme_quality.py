import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"


def rel_luminance(value: str) -> float:
    """Calculate relative luminance for WCAG contrast."""

    def channel(part: int) -> float:
        scaled = part / 255
        return scaled / 12.92 if scaled <= 0.03928 else ((scaled + 0.055) / 1.055) ** 2.4

    value = value.lstrip("#")
    r, g, b = (channel(int(value[i : i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(left: str, right: str) -> float:
    """Calculate WCAG 2 contrast ratio."""
    a, b = sorted((rel_luminance(left), rel_luminance(right)), reverse=True)
    return (a + 0.05) / (b + 0.05)


class DreamcoderThemeQualityTest(unittest.TestCase):
    def setUp(self):
        self.modes = json.loads(TOKENS.read_text())["modes"]

    def test_dark_uses_black_oled_scale(self):
        dark = self.modes["dark"]
        self.assertEqual(dark["name"], "Dreamcoder Dark")
        self.assertEqual(dark["bg"], "#000000")
        self.assertEqual(dark["surface0"], "#0B0B0B")
        self.assertEqual(dark["surface1"], "#0D0D0F")
        self.assertEqual(dark["surface2"], "#1F1F1F")
        self.assertEqual(dark["surface3"], "#2E2E2E")
        self.assertEqual(dark["focus"], "#3B82F6")

    def test_light_has_stronger_editor_readability_tiers(self):
        light = self.modes["light"]
        self.assertEqual(light["surface0"], "#fff7ea")
        self.assertEqual(light["surface2"], "#c8ad89")
        self.assertGreaterEqual(contrast(light["subtle"], light["bg"]), 4.5)
        self.assertGreaterEqual(contrast(light["comment"], light["bg"]), 4.5)

    def test_light_selection_uses_explicit_pair(self):
        light = self.modes["light"]
        self.assertEqual(light["selection_bg"], "#decbb1")
        self.assertEqual(light["selection_fg"], light["text"])
        self.assertGreaterEqual(contrast(light["selection_fg"], light["selection_bg"]), 7.0)

    def test_dark_has_text_heading_and_surface3(self):
        dark = self.modes["dark"]
        self.assertIn("text_heading", dark)
        self.assertIn("surface3", dark)
        self.assertGreater(
            contrast(dark["text_heading"], dark["bg"]), contrast(dark["text"], dark["bg"])
        )


if __name__ == "__main__":
    unittest.main()
