"""Keep Bat's compiled theme cache in step with generated TextMate sources."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .settings import ThemePaths


class BatCacheError(RuntimeError):
    """Bat could not produce a usable compiled cache."""


def ensure_bat_cache(paths: ThemePaths) -> str:
    """Build missing/stale caches, ignoring personal Bat command-line defaults.

    BAT_CACHE_PATH wins over XDG_CACHE_HOME/bat, then HOME/.cache/bat.
    Both compiled files must be nonempty and at least as new as every theme
    source. Call only after the active theme and both variants are written.
    """
    executable = shutil.which("bat")
    if executable is None:
        return "skipped (bat not installed)"
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    cache = Path(os.environ.get("BAT_CACHE_PATH", cache_home / "bat"))
    compiled = [cache / name for name in ("themes.bin", "syntaxes.bin")]
    try:
        newest_source = max(
            (path.stat().st_mtime_ns for path in paths.bat_theme_dir.rglob("*.tmTheme")),
            default=0,
        )
        if all(
            path.is_file() and path.stat().st_size > 0 and path.stat().st_mtime_ns >= newest_source
            for path in compiled
        ):
            return "unchanged"
        result = subprocess.run(
            [
                executable,
                "cache",
                "--build",
                "--source",
                str(paths.bat_theme_dir.parent),
                "--target",
                str(cache),
            ],
            env={**os.environ, "BAT_CONFIG_PATH": os.devnull, "BAT_CACHE_PATH": str(cache)},
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
            raise BatCacheError(f"bat cache build failed (exit {result.returncode}): {detail}")
        invalid = [path.name for path in compiled if not path.is_file() or path.stat().st_size == 0]
        if invalid:
            raise BatCacheError(
                "bat cache build failed: missing or empty cache files: " + ", ".join(invalid)
            )
    except (OSError, subprocess.SubprocessError) as exc:
        raise BatCacheError(f"bat cache build failed: {exc}") from exc
    return "rebuilt"
