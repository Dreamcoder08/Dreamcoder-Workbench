"""Check optional Zsh hooks without loading an interactive startup file."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ZshOptionalFunctionsTest(unittest.TestCase):
    def test_bun_completion_requires_nonempty_regular_file(self):
        runner = shutil.which("zsh")
        if runner is None:
            self.skipTest("zsh unavailable")
        initialization = next(
            line
            for line in (ROOT / "DreamcoderShell/.zshrc").read_text().splitlines()
            if 'source "${BUN_INSTALL}/_bun"' in line
        )
        for kind in ("directory", "regular", "empty", "missing", "symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                completion = root / "_bun"
                if kind == "directory":
                    completion.mkdir()
                    (completion / "marker.zsh").write_text('printf "unexpected\\n"; : > "$2"\n')
                    self.assertGreater(completion.stat().st_size, 0)
                elif kind == "regular":
                    completion.write_text("printf 'bun completion loaded\\n'\n")
                elif kind == "empty":
                    completion.touch()
                elif kind == "symlink":
                    target = root / "completion.zsh"
                    target.write_text("printf 'bun completion loaded\\n'\n")
                    completion.symlink_to(target)
                before = {
                    path.relative_to(root): path.read_bytes()
                    for path in root.rglob("*")
                    if path.is_file()
                }
                entries = set(root.rglob("*"))
                result = subprocess.run(
                    [
                        runner,
                        "-f",
                        "-c",
                        f'BUN_INSTALL="$1"\n{initialization}',
                        "zsh-bun-test",
                        str(root),
                        str(root / "side-effect"),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                sourced = kind in ("regular", "symlink")
                self.assertEqual(result.returncode, 0 if sourced else 1)
                self.assertEqual(result.stdout, "bun completion loaded\n" if sourced else "")
                self.assertEqual(result.stderr, "")
                self.assertEqual(set(root.rglob("*")), entries)
                self.assertFalse((root / "side-effect").exists())
                self.assertEqual(
                    {
                        path.relative_to(root): path.read_bytes()
                        for path in root.rglob("*")
                        if path.is_file()
                    },
                    before,
                )

    def test_starship_transience_with_and_without_optional_function(self):
        runner = shutil.which("zsh")
        if runner is None:
            self.skipTest("zsh unavailable")
        initialization = next(
            line
            for line in (ROOT / "DreamcoderShell/.zshrc").read_text().splitlines()
            if "starship init zsh" in line
        )
        for present in (False, True):
            with self.subTest(function_present=present):
                definition = (
                    "enable_transience() { printf 'transience enabled\\n'; }" if present else ""
                )
                script = (
                    "starship() {\n"
                    "  [[ \"$*\" == 'init zsh' ]] || return 71\n"
                    "  printf '%s\\n' \"$INIT_CODE\"\n"
                    "}\n"
                    "INIT_CODE=$1\n"
                    f"{initialization}\n"
                    "status_code=$?\n"
                    "printf 'status=%s\\n' \"$status_code\"\n"
                )
                result = subprocess.run(
                    [runner, "-f", "-c", script, "zsh-hook-test", definition],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stderr, "")
                self.assertEqual(
                    result.stdout,
                    "transience enabled\nstatus=0\n" if present else "status=1\n",
                )
