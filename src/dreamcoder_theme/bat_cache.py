"""Maintain Bat's compiled cache after theme sources have been written."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import ExitStack
from pathlib import Path

from .settings import ThemePaths


class BatCacheError(RuntimeError):
    """A present Bat installation could not compile its theme sources."""


def ensure_bat_cache(paths: ThemePaths) -> str:
    """Repair missing/stale binaries without rebuilding an up-to-date cache."""
    bat = shutil.which("bat")
    if bat is None:
        return "skipped (bat not installed)"
    cache = Path(
        os.environ.get(
            "BAT_CACHE_PATH",
            Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "bat",
        )
    )
    command = [bat, "cache", "--build"]
    try:
        binaries = [cache / name for name in ("themes.bin", "syntaxes.bin")]
        sources = [path for path in paths.bat_theme_dir.rglob("*") if path.is_file()]
        if all(path.is_file() for path in binaries):
            oldest_cache = min(path.stat().st_mtime_ns for path in binaries)
            if all(path.stat().st_mtime_ns <= oldest_cache for path in sources):
                return "unchanged"
        with ExitStack() as stack:
            source_root = paths.bat_theme_dir.parent
            if paths.bat_theme_dir.name != "themes":
                # Bat requires a themes/ child of --source, even for custom destinations.
                source_root = Path(stack.enter_context(tempfile.TemporaryDirectory()))
                (source_root / "themes").symlink_to(paths.bat_theme_dir.resolve())
            command += ["--source", str(source_root), "--target", str(cache)]
            result = subprocess.run(
                command,
                env=dict(os.environ, BAT_CONFIG_PATH=os.devnull),
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
                raise BatCacheError(
                    f"bat cache build failed (exit {result.returncode}): {detail}. "
                    f"Check themes in {paths.bat_theme_dir} and cache permissions at {cache}, "
                    "then rerun dreamcoder sync."
                )
    except OSError as exc:
        raise BatCacheError(
            f"bat cache build failed: {exc}. Check themes in {paths.bat_theme_dir} "
            f"and cache permissions at {cache}, then rerun dreamcoder sync."
        ) from exc
    return "rebuilt"
