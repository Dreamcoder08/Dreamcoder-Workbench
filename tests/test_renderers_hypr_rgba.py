"""Hyprland rgba() converter regression tests.

Covers the zfill-vs-truncate bug in ``_rgba_to_argb``: RGB channels >= 100 were
padded instead of clamped to 2 hex digits, producing invalid 10-char rgba()
values (e.g. rgba(13811588ed)) that Hyprland rejects.
"""

from __future__ import annotations

import unittest

from dreamcoder_theme.renderers_hypr_waybar_rofi import _rgba_to_argb


class RgbaToArgbTest(unittest.TestCase):
    def test_dark_inactive_border(self) -> None:
        # The exact token that produced rgba(8210111780) before the fix.
        self.assertEqual(_rgba_to_argb("rgba(82, 101, 117, 0.50)"), "rgba(52657580)")

    def test_light_inactive_border(self) -> None:
        # 3-digit channels must be clamped to 2 hex digits, not padded.
        self.assertEqual(_rgba_to_argb("rgba(138, 115, 88, 0.93)"), "rgba(8a7358ed)")

    def test_muted_translucent_border(self) -> None:
        self.assertEqual(_rgba_to_argb("rgba(167, 148, 122, 0.87)"), "rgba(a7947ade)")

    def test_all_channels_large(self) -> None:
        self.assertEqual(_rgba_to_argb("rgba(255, 254, 253, 1.0)"), "rgba(fffefdff)")

    def test_already_rrgbbaa_passes_through(self) -> None:
        # rgba(000000ff) style values (no commas) are already canonical.
        self.assertEqual(_rgba_to_argb("rgba(000000ff)"), "rgba(000000ff)")

    def test_output_is_exactly_eight_hex_digits(self) -> None:
        for value in (
            "rgba(82, 101, 117, 0.50)",
            "rgba(138, 115, 88, 0.93)",
            "rgba(167, 148, 122, 0.87)",
        ):
            out = _rgba_to_argb(value)
            inner = out.removeprefix("rgba(").removesuffix(")")
            self.assertEqual(len(inner), 8, f"{value} -> {out}")


if __name__ == "__main__":
    unittest.main()
