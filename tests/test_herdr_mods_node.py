"""Run the Herdr mod helper tests (node --test) as part of the Python suite."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_herdr_mod_helpers_pass_under_node() -> None:
    tests = sorted(str(p) for p in (ROOT / "tests/herdr_mods").glob("*.test.mjs"))
    assert tests, "no Herdr mod helper tests found"
    result = subprocess.run(
        ["node", "--test", *tests], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
