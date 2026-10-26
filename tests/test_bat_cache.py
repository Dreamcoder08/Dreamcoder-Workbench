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
        assert themes.returncode == 0, themes.stdout + themes.stderr
        assert themes.stderr == ""
        assert {"Dreamcoder", "Dreamcoder-Dark", "Dreamcoder-Light"} <= set(
            themes.stdout.splitlines()
        )
        cache.unlink()


@pytest.mark.skipif(shutil.which("bat") is None, reason="optional bat not installed")
@pytest.mark.parametrize("mode", ["dark", "light"])
def test_public_sync_preserves_mode_and_rebuilds_only_stale_cache(tmp_path, mode):
    result = run_sync(tmp_path, mode)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert f"Synced Dreamcoder {mode} identity\n" in result.stdout
    cache = tmp_path / "cache/bat/themes.bin"
    timestamp = cache.stat().st_mtime_ns
    result = run_sync(tmp_path, mode)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert "Bat cache: unchanged\n" in result.stdout
    assert cache.stat().st_mtime_ns == timestamp
    source = tmp_path / "config/bat/themes/Dreamcoder.tmTheme"
    os.utime(cache, ns=(1, source.stat().st_mtime_ns - 1))
    result = run_sync(tmp_path, mode)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert "Bat cache: rebuilt\n" in result.stdout
    assert cache.stat().st_mtime_ns >= source.stat().st_mtime_ns


@pytest.mark.parametrize("failure", ["exit", "missing", "empty"])
def test_public_sync_reports_failed_or_incomplete_build(tmp_path, monkeypatch, failure):
    binary = tmp_path / "bin/bat"
    binary.parent.mkdir()
    binary.write_text(
        f"#!{sys.executable}\n"
        "import os, pathlib, sys\n"
        "assert os.environ['BAT_CONFIG_PATH'] == os.devnull\n"
        "source = pathlib.Path(sys.argv[sys.argv.index('--source') + 1])\n"
        "assert len(list((source / 'themes').glob('Dreamcoder*.tmTheme'))) == 3\n"
        + (
            "print('broken syntax', file=sys.stderr)\nsys.exit(7)\n"
            if failure == "exit"
            else "target = pathlib.Path(sys.argv[sys.argv.index('--target') + 1])\n"
            "target.mkdir(parents=True, exist_ok=True)\n"
            + (
                "(target / 'themes.bin').touch()\n(target / 'syntaxes.bin').touch()\n"
                if failure == "empty"
                else ""
            )
        )
    )
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary.parent))
    result = run_sync(tmp_path)
    assert result.returncode == 1
    assert result.stdout == "✓ Generated src/dreamcoder_theme/palette_tokens.py\n"
    if failure == "exit":
        assert result.stderr == "bat cache build failed (exit 7): broken syntax\n"
    else:
        assert result.stderr == (
            "bat cache build failed: missing or empty cache files: themes.bin, syntaxes.bin\n"
        )
    assert "Traceback" not in result.stderr


def test_public_sync_skips_optional_bat(tmp_path, monkeypatch):
    binary_dir = tmp_path / "empty-bin"
    binary_dir.mkdir()
    monkeypatch.setenv("PATH", str(binary_dir))
    result = run_sync(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    assert "Bat cache: skipped (bat not installed)\n" in result.stdout
    assert not (tmp_path / "cache/bat").exists()
    assert (tmp_path / "config/bat/themes/Dreamcoder.tmTheme").is_file()


def test_cache_fresh_stale_and_unchanged(bat_env):
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


@pytest.mark.parametrize("fallback", ["xdg", "home"])
def test_cache_destination_fallbacks(bat_env, monkeypatch, fallback):
    monkeypatch.delenv("BAT_CACHE_PATH")
    expected = bat_env / "cache/bat"
    if fallback == "home":
        monkeypatch.delenv("XDG_CACHE_HOME")
        expected = bat_env / ".cache/bat"

    def build(command, **kwargs):
        assert command[-2:] == ["--target", str(expected)]
        expected.mkdir(parents=True)
        for name in ("themes.bin", "syntaxes.bin"):
            (expected / name).write_bytes(b"compiled")
        return subprocess.CompletedProcess(command, 0, "", "")

    with (
        mock.patch("dreamcoder_theme.bat_cache.shutil.which", return_value="bat"),
        mock.patch("dreamcoder_theme.bat_cache.subprocess.run", side_effect=build),
    ):
        assert ensure_bat_cache(theme_paths()) == "rebuilt"


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
