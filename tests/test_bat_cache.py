"""Public sync/cache lifecycle checks; every subprocess uses isolated roots."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from unittest import mock

import pytest
from test_pi_theme_generation import run_sync

from dreamcoder_theme.bat_cache import BatCacheError, ensure_bat_cache
from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderers import codex_tmtheme_content
from dreamcoder_theme.settings import theme_paths


@pytest.fixture
def bat_env(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("BAT_CACHE_PATH", str(tmp_path / "cache/bat"))
    monkeypatch.setenv("BAT_THEME_DIR", str(tmp_path / "config/bat/themes"))
    return tmp_path


@pytest.mark.skipif(shutil.which("bat") is None, reason="optional bat not installed")
@pytest.mark.parametrize("existing_sources", [False, True])
def test_public_sync_builds_after_all_writes_and_repairs_missing_cache(tmp_path, existing_sources):
    if existing_sources:
        assert run_sync(tmp_path, "light").returncode == 0
    for _ in range(2):
        result = run_sync(tmp_path, "light")
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == ""
        cache = tmp_path / "cache/bat/themes.bin"
        assert cache.is_file()
        env = dict(os.environ, BAT_CONFIG_PATH=os.devnull, BAT_CACHE_PATH=str(cache.parent))
        themes = subprocess.run(
            [shutil.which("bat"), "--list-themes"],
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        assert themes.returncode == 0
        assert themes.stderr == ""
        assert {"Dreamcoder", "Dreamcoder-Dark", "Dreamcoder-Light"} <= set(
            themes.stdout.splitlines()
        )
        before = {path.name: path.read_bytes() for path in cache.parent.iterdir()}
        modified = cache.stat().st_mtime_ns
        unchanged = run_sync(tmp_path, "light")
        assert unchanged.returncode == 0
        assert unchanged.stderr == ""
        assert cache.stat().st_mtime_ns == modified
        assert {path.name: path.read_bytes() for path in cache.parent.iterdir()} == before
        cache.unlink()


@pytest.mark.parametrize("xdg_default", [False, True])
def test_cache_fresh_stale_and_unchanged(bat_env, monkeypatch, xdg_default):
    if xdg_default:
        monkeypatch.delenv("BAT_CACHE_PATH")
        monkeypatch.delenv("BAT_THEME_DIR")
    paths = theme_paths()
    paths.bat_theme_dir.mkdir(parents=True)
    source = paths.bat_theme_dir / "Dreamcoder.tmTheme"
    source.write_text("theme")
    cache = bat_env / "cache/bat"

    def build(*args, **kwargs):
        assert args[0][-4:] == ["--source", str(paths.bat_theme_dir.parent), "--target", str(cache)]
        assert kwargs["env"]["BAT_CONFIG_PATH"] == os.devnull
        cache.mkdir(parents=True, exist_ok=True)
        for name in ("themes.bin", "syntaxes.bin"):
            (cache / name).write_text("compiled")
        return subprocess.CompletedProcess(args[0], 0, "", "")

    with (
        mock.patch("dreamcoder_theme.bat_cache.shutil.which", return_value="bat"),
        mock.patch("dreamcoder_theme.bat_cache.subprocess.run", side_effect=build) as runner,
    ):
        assert ensure_bat_cache(paths) == "rebuilt"
        assert ensure_bat_cache(paths) == "unchanged"
        assert runner.call_count == 1
        os.utime(source, ns=(1, (cache / "themes.bin").stat().st_mtime_ns + 1000000))
        assert ensure_bat_cache(paths) == "rebuilt"
        assert runner.call_count == 2
        (cache / "syntaxes.bin").unlink()
        assert ensure_bat_cache(paths) == "rebuilt"
        assert runner.call_count == 3


def test_optional_absence_and_build_failure(bat_env):
    with mock.patch("dreamcoder_theme.bat_cache.shutil.which", return_value=None):
        assert ensure_bat_cache(theme_paths()) == "skipped (bat not installed)"
    with (
        mock.patch("dreamcoder_theme.bat_cache.shutil.which", return_value="bat"),
        mock.patch(
            "dreamcoder_theme.bat_cache.subprocess.run",
            return_value=subprocess.CompletedProcess([], 7, "", "broken syntax"),
        ),
        pytest.raises(BatCacheError, match=r"bat cache build failed.*broken syntax"),
    ):
        ensure_bat_cache(theme_paths())


@pytest.mark.skipif(shutil.which("bat") is None, reason="optional bat not installed")
def test_custom_theme_directory(bat_env, monkeypatch):
    monkeypatch.setenv("BAT_THEME_DIR", str(bat_env / "custom-colors"))
    paths = theme_paths()
    paths.bat_theme_dir.mkdir()
    (paths.bat_theme_dir / "Dreamcoder.tmTheme").write_text(codex_tmtheme_content(VARIANTS["dark"]))
    assert ensure_bat_cache(paths) == "rebuilt"
    assert ensure_bat_cache(paths) == "unchanged"


def test_public_build_failure_is_actionable(tmp_path, monkeypatch):
    binary_dir = tmp_path / "bin"
    binary_dir.mkdir()
    bat = binary_dir / "bat"
    bat.write_text(
        f"#!{sys.executable}\nimport sys\nsys.stderr.write('broken syntax')\nsys.exit(7)\n"
    )
    bat.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary_dir) + os.pathsep + os.environ["PATH"])
    result = run_sync(tmp_path, "light")
    assert result.returncode == 1
    assert result.stdout == "✓ Generated src/dreamcoder_theme/palette_tokens.py\n"
    assert result.stderr == (
        "bat cache build failed (exit 7): broken syntax. "
        f"Check themes in {tmp_path / 'config/bat/themes'} and cache permissions at "
        f"{tmp_path / 'cache/bat'}, then rerun dreamcoder sync.\n"
    )
    assert not (tmp_path / "cache/bat/themes.bin").exists()
    before = {p.name: p.read_bytes() for p in (tmp_path / "config/bat/themes").iterdir()}
    repeated = run_sync(tmp_path, "light")
    assert (repeated.returncode, repeated.stdout, repeated.stderr) == (
        result.returncode,
        result.stdout,
        result.stderr,
    )
    assert {p.name: p.read_bytes() for p in (tmp_path / "config/bat/themes").iterdir()} == before
