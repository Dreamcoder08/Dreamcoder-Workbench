"""Neovim syntax readability tests for Dreamcoder themes."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"

from dreamcoder_theme.renderers_extra_nvim import nvim_content


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


def color_distance(left: str, right: str) -> float:
    """Calculate simple RGB distance between two foreground colors."""
    left = left.lstrip("#")
    right = right.lstrip("#")
    left_rgb = tuple(int(left[i : i + 2], 16) for i in (0, 2, 4))
    right_rgb = tuple(int(right[i : i + 2], 16) for i in (0, 2, 4))
    return sum((a - b) ** 2 for a, b in zip(left_rgb, right_rgb)) ** 0.5


class NvimReadabilityTest(unittest.TestCase):
    """Tests for Neovim syntax highlight readability."""

    def setUp(self):
        self.modes = json.loads(TOKENS.read_text())["modes"]

    def test_dark_comment_has_sufficient_contrast_against_background(self):
        """Dark mode comment must be clearly distinguishable from background."""
        dark = self.modes["dark"]
        bg = dark["bg"]
        comment = dark["comment"]

        # WCAG AA minimum
        self.assertGreaterEqual(
            contrast(comment, bg), 4.5, f"Dark comment {comment} vs bg {bg} lacks WCAG AA contrast"
        )

    def test_dark_comment_distinct_from_subtle(self):
        """Dark mode comment and subtle must be visually distinguishable."""
        dark = self.modes["dark"]
        comment = dark["comment"]
        subtle = dark["subtle"]

        # Should have at least 1.5:1 contrast to be distinguishable
        self.assertGreaterEqual(
            contrast(comment, subtle), 1.5, f"Dark comment {comment} too similar to subtle {subtle}"
        )

    def test_light_comment_distinct_from_muted(self):
        """Light mode comment and muted must be visually distinguishable."""
        light = self.modes["light"]
        comment = light["comment"]
        muted = light["muted"]

        # Should have at least 2:1 contrast to be clearly distinguishable
        self.assertGreaterEqual(
            contrast(comment, muted), 2.0, f"Light comment {comment} too similar to muted {muted}"
        )

    def test_dark_string_has_sufficient_contrast_against_background(self):
        """Dark mode string (sage) must have good contrast."""
        dark = self.modes["dark"]
        bg = dark["bg"]
        sage = dark["sage"]

        self.assertGreaterEqual(
            contrast(sage, bg), 4.5, f"Dark string {sage} vs bg {bg} lacks WCAG AA contrast"
        )

    def test_dark_string_distinct_from_comment(self):
        """Dark mode string and comment must be distinguishable."""
        dark = self.modes["dark"]
        sage = dark["sage"]
        comment = dark["comment"]

        # Strings should be clearly different from comments
        self.assertGreaterEqual(
            color_distance(sage, comment),
            80,
            f"Dark string {sage} too similar to comment {comment}",
        )

    def test_dark_diagnostic_distinct_from_comment(self):
        """Dark mode diagnostic should be distinguishable from comment."""
        dark = self.modes["dark"]
        diagnostic = dark["diagnostic"]
        comment = dark["comment"]

        self.assertGreaterEqual(
            color_distance(diagnostic, comment),
            80,
            f"Dark diagnostic {diagnostic} too similar to comment {comment}",
        )

    def test_light_normal_background_is_opaque(self):
        for mode in ("light",):
            palette = self.modes.get(mode)
            if palette is None:
                continue
            rendered = nvim_content(palette)
            normal_block = rendered.split('"Normal", {', 1)[1].split("})", 1)[0]
            sign_block = rendered.split('"SignColumn", {', 1)[1].split("})", 1)[0]
            self.assertIn(f'bg = "{palette["bg"]}"', normal_block)
            self.assertIn(f'bg = "{palette["bg"]}"', sign_block)

    def test_dark_content_background_is_opaque_black(self):
        rendered = nvim_content(self.modes["dark"])
        for group in ("Normal", "SignColumn"):
            block = rendered.split(f'"{group}", {{', 1)[1].split("})", 1)[0]
            self.assertIn('bg = "#000000"', block)

    def test_dark_floating_surfaces_stay_near_black(self):
        dark = self.modes["dark"]
        rendered = nvim_content(dark)
        self.assertNotEqual(dark["surface0"], "#000000")
        for group in ("NormalFloat", "FloatBorder"):
            block = rendered.split(f'"{group}", {{', 1)[1].split("})", 1)[0]
            self.assertIn(f'bg = "{dark["surface0"]}"', block)


if __name__ == "__main__":
    unittest.main()
