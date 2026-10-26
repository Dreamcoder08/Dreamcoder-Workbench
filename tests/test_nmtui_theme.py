"""Exercise only a fake nmtui: never change network connections or load startup files."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "DreamcoderShell/.local/bin/dreamcoder-nmtui"
FISH = ROOT / "DreamcoderShell/.config/fish/functions/nmtui.fish"
ZSH = ROOT / "DreamcoderShell/.zshrc"
COMMON = set(
    [
        "root",
        "border",
        "window",
        "shadow",
        "title",
        "button",
        "checkbox",
        "entry",
        "label",
        "listbox",
        "textbox",
        "helpline",
        "roottext",
        "emptyscale",
        "compactbutton",
    ]
)
FOCUS = set(
    [
        "actbutton",
        "actcheckbox",
        "actlistbox",
        "acttextbox",
        "fullscale",
        "sellistbox",
        "actsellistbox",
    ]
)


class NmtuiThemeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dreamcoder-nmtui-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        self.env = {
            "HOME": str(self.home),
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "XDG_CACHE_HOME": str(self.home / "cache"),
            "UNRELATED": "unchanged",
        }
        self.fake = self.bin / "nmtui"
        self.fake.write_text(
            f"#!{sys.executable}\nimport json, os, sys\n"
            "print(json.dumps({'argv': sys.argv[1:], 'env': dict(os.environ)}, sort_keys=True))\n"
            "sys.stderr.write(os.environ.get('FAKE_STDERR', ''))\n"
            "sys.exit(int(os.environ.get('FAKE_EXIT', '0')))\n"
        )
        self.fake.chmod(0o755)

    def run_wrapper(self, *args):
        return subprocess.run(
            [str(LAUNCHER), *args], env=self.env, capture_output=True, text=True, check=False
        )

    def cache(self, text, default=False):
        base = self.home / ".cache" if default else Path(self.env["XDG_CACHE_HOME"])
        path = base / "dreamcoder/cursor-cli.env"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def assert_palette(self, result, focus):
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        env = json.loads(result.stdout)["env"]
        roles = dict(item.split("=", 1) for item in env["NEWT_COLORS"].split())
        self.assertEqual(set(roles), COMMON | FOCUS | {"disentry"})
        for role in COMMON:
            self.assertEqual(roles[role], "default,default", role)
        for role in FOCUS:
            self.assertEqual(roles[role], f"{focus},default", role)
        self.assertEqual(roles["disentry"], "gray,default")
        self.assertEqual(
            dict(item.split("=", 1) for item in env["NMT_NEWT_COLORS"].split()),
            {
                "badLabel": "red,default",
                "plainLabel": "default,default",
                "disabledButton": "gray,default",
                "textboxWithBackground": "default,default",
            },
        )
        self.assertEqual(env["UNRELATED"], "unchanged")

    def test_modes_and_invalid_environment(self):
        for mode, focus in [
            ("light", "brown"),
            ("dark", "blue"),
            ("invalid", "blue"),
            ("", "blue"),
        ]:
            with self.subTest(mode=mode):
                self.env["DREAMCODER_THEME_MODE"] = mode
                self.assert_palette(self.run_wrapper(), focus)
        del self.env["DREAMCODER_THEME_MODE"]
        self.assert_palette(self.run_wrapper(), "blue")

    def test_default_mono_in_light_and_dark(self):
        for mode, focus in [("light", "brown"), ("dark", "blue")]:
            with self.subTest(mode=mode):
                self.env["DREAMCODER_THEME_MODE"] = mode
                result = self.run_wrapper()
                self.assert_palette(result, focus)
                self.assertEqual(json.loads(result.stdout)["env"].get("NEWT_MONO"), "1")
                self.assertEqual(json.loads(result.stdout)["argv"], [])
                self.assertNotIn("NEWT_MONO", self.env)

    def test_explicit_mono_including_empty(self):
        for mode, focus in [("light", "brown"), ("dark", "blue")]:
            for value in ["", "0", "1"]:
                with self.subTest(mode=mode, value=value):
                    self.env.update(DREAMCODER_THEME_MODE=mode, NEWT_MONO=value)
                    result = self.run_wrapper()
                    self.assert_palette(result, focus)
                    self.assertEqual(json.loads(result.stdout)["env"]["NEWT_MONO"], value)
                    self.assertEqual(json.loads(result.stdout)["argv"], [])

    def test_persisted_mode_wins_and_default_cache_location(self):
        for value in ["light", '"light"', "'light'"]:
            with self.subTest(value=value):
                self.env["DREAMCODER_THEME_MODE"] = "dark"
                self.cache(f"export DREAMCODER_THEME_MODE={value}\n")
                self.assert_palette(self.run_wrapper(), "brown")
        self.env["DREAMCODER_THEME_MODE"] = "light"
        self.cache('export DREAMCODER_THEME_MODE="dark"\n', default=True)
        del self.env["XDG_CACHE_HOME"]
        self.assert_palette(self.run_wrapper(), "blue")
        self.cache(
            "export DREAMCODER_THEME_MODE=light\nexport DREAMCODER_THEME_MODE=dark\nexport DREAMCODER_THEME_MODE=invalid",
            default=True,
        )
        self.assert_palette(self.run_wrapper(), "blue")

    def test_malformed_cache_is_inert_and_unchanged(self):
        marker = self.home / "should-not-exist"
        text = (
            f'export DREAMCODER_THEME_MODE=$(touch "{marker}")\n'
            'export DREAMCODER_THEME_MODE="light\nDREAMCODER_THEME_MODE=light\n'
            "export DREAMCODER_THEME_MODE=light; false\n"
        )
        path = self.cache(text)
        self.assert_palette(self.run_wrapper(), "blue")
        self.assertFalse(marker.exists())
        self.assertEqual(path.read_text(), text)

    def test_explicit_family_overrides_including_empty(self):
        for family, other in [("NEWT", "NMT_NEWT"), ("NMT_NEWT", "NEWT")]:
            for suffix in ["COLORS", "COLORS_FILE"]:
                for value in ["", "custom value with spaces"]:
                    with self.subTest(family=family, suffix=suffix, value=value):
                        key = f"{family}_{suffix}"
                        self.env[key] = value
                        result = self.run_wrapper()
                        self.assertEqual((result.returncode, result.stderr), (0, ""))
                        env = json.loads(result.stdout)["env"]
                        self.assertEqual(env[key], value)
                        self.assertNotIn("NEWT_MONO", env)
                        if suffix == "COLORS_FILE":
                            self.assertNotIn(f"{family}_COLORS", env)
                        self.assertIn(f"{other}_COLORS", env)
                        for name, original in self.env.items():
                            self.assertEqual(env[name], original)
                        del self.env[key]

    def test_exact_forwarding_including_help(self):
        self.env.update(FAKE_EXIT="23", FAKE_STDERR="exact error\n")
        for args in [[], ["--help"], ["edit", "a b", "", "*", "--unknown"]]:
            with self.subTest(args=args):
                result = self.run_wrapper(*args)
                self.assertEqual((result.returncode, result.stderr), (23, "exact error\n"))
                payload = json.loads(result.stdout)
                self.assertEqual(payload["argv"], args)
                self.assertEqual(result.stdout, json.dumps(payload, sort_keys=True) + "\n")

    def test_shell_routing_and_fallback_without_loading_startup(self):
        for shell in ["fish", "zsh"]:
            runner = shutil.which(shell)
            if runner is None:
                self.skipTest(f"{shell} unavailable; inspect fallback structure")
            if shell == "fish":
                definition = FISH.read_text()
                command = [runner, "--no-config", "-c"]
            else:
                source = ZSH.read_text()
                definition = source[source.index("nmtui() {") :].split("\n}", 1)[0] + "\n}"
                command = [runner, "-f", "-c"]
            self.assertIn("command nmtui", definition)
            script = definition + "\nnmtui 'a b' '' --help"
            for available in [False, True]:
                with self.subTest(shell=shell, wrapper=available):
                    if available:
                        wrapper = self.bin / "dreamcoder-nmtui"
                        wrapper.symlink_to(LAUNCHER)
                    self.env.update(FAKE_EXIT="19", FAKE_STDERR="shell error\n")
                    result = subprocess.run(
                        [*command, script],
                        env=self.env,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual((result.returncode, result.stderr), (19, "shell error\n"))
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["argv"], ["a b", "", "--help"])
                    self.assertEqual("NEWT_COLORS" in payload["env"], available)
                    if available:
                        wrapper.unlink()

    def test_waybar_only_changes_network_launcher(self):
        content = (ROOT / "DreamcoderWaybar/.config/waybar/config.jsonc").read_text()
        self.assertIn('"on-click": "kitty dreamcoder-nmtui"', content)
        self.assertIn('"on-click": "pactl set-sink-mute @DEFAULT_SINK@ toggle"', content)


if __name__ == "__main__":
    unittest.main()
