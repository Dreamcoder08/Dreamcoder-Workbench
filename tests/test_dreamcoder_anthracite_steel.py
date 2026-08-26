import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"


class DreamcoderDarkIdentityTest(unittest.TestCase):
    """Verify Dreamcoder Dark identity and canonical runtime roles."""

    def setUp(self):
        tokens = json.loads(TOKENS.read_text())
        self.dark = tokens["modes"]["dark"]

    def test_dark_mode_uses_surface_policy_ladder(self):
        self.assertEqual(self.dark["name"], "Dreamcoder Dark")
        self.assertEqual(self.dark["bg"], "#000000")
        self.assertEqual(
            [self.dark[f"surface{index}"] for index in range(4)],
            ["#060608", "#0D0D11", "#16161D", "#1E1E24"],
        )
        self.assertEqual(self.dark["hover"], "#22222D")

    def test_dark_mode_has_accessible_runtime_semantics(self):
        self.assertEqual(self.dark["accent"], "#A5B4FC")
        self.assertEqual(self.dark["focus"], "#3B82F6")
        self.assertEqual(self.dark["error"], "#FB8585")
        self.assertEqual(self.dark["warning"], "#FBBF24")
        self.assertEqual(self.dark["success"], "#34D399")

    def test_dark_mode_keeps_requested_oled_aliases(self):
        aliases = self.dark["aliases"]
        self.assertEqual(aliases["brand"], "#6366F1")
        self.assertEqual(aliases["text_muted"], "#64748B")
        self.assertEqual(aliases["border_subtle"], "#12121A")
        self.assertEqual(aliases["border_medium"], "#1F1F2B")
        self.assertEqual(aliases["error_requested"], "#F87171")

    def test_dark_mode_owns_its_oled_surface_policy(self):
        policy = self.dark["surface_policy"]
        self.assertEqual(policy["scroll_surface"], "surface0")
        self.assertEqual(
            policy["pure_black_policy"],
            {
                "canvas": True,
                "functional_surfaces": False,
                "scrollable_surfaces": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
