"""finish-wallpaper.sh: crop, linear-light upscale, paper grain, dither.

Spec: odd/tasks/dreamcoder-light-coherence.md, T6 (S1, S3, S7).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FINISH = ROOT / "scripts/finish-wallpaper.sh"
CHECK = ROOT / "scripts/check-wallpaper.py"

pytestmark = pytest.mark.skipif(shutil.which("magick") is None, reason="ImageMagick not installed")


def _run(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, check=False)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "source.png"
    subprocess.run(
        ["magick", "-size", "1536x1024", "gradient:#f2eee9-#e3ddd5", str(path)], check=True
    )
    return path


def test_finished_image_is_4k_and_meets_the_light_contract(source: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    result = _run(FINISH, source, out)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"finished {out}"
    size = _run("magick", "identify", "-format", "%w %h %[depth]", out).stdout
    assert size == "3840 2160 8"
    check = _run("python", CHECK, "--mode", "light", out)
    assert check.returncode == 0, check.stdout + check.stderr


def test_finishing_is_deterministic(source: Path, tmp_path: Path) -> None:
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    assert _run(FINISH, source, a).returncode == 0
    assert _run(FINISH, source, b).returncode == 0
    assert a.read_bytes() == b.read_bytes()


def test_missing_input_fails_without_writing(tmp_path: Path) -> None:
    out = tmp_path / "out.png"
    result = _run(FINISH, tmp_path / "nope.png", out)
    assert result.returncode == 1
    assert result.stderr.strip() == f"finish-wallpaper: input not found: {tmp_path / 'nope.png'}"
    assert not out.exists()


def test_usage_error_exits_2() -> None:
    result = _run(FINISH)
    assert result.returncode == 2
    assert result.stderr.startswith("usage: finish-wallpaper.sh INPUT OUTPUT")
