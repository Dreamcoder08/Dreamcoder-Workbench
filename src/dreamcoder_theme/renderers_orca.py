"""Orca terminal theme entry, derived from the standard ANSI mapping.

Orca (an Electron-based dev IDE, unrelated to the GNOME screen reader) keeps
its own list of named terminal color schemes in its per-profile settings
file rather than reading a checked-in theme file, so there is no
repository-variant output here — only the same dict shape used to populate
``settings.terminalCustomThemes`` in that file.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .palette import ansi

_DEFAULT_DATA_PATH = "~/.config/orca/profiles/local-default/orca-data.json"


def orca_terminal_theme(c: dict[str, str]) -> dict[str, str]:
    """Build one Orca terminalCustomThemes entry from a Dreamcoder palette."""
    p = ansi(c)
    return {
        "name": c["name"],
        "background": c["bg"],
        "foreground": c["text"],
        "cursor": c["accent"],
        "cursorAccent": c["on_accent"],
        "selectionBackground": c["selection_bg"],
        "selectionForeground": c["selection_fg"],
        "black": p[0],
        "red": p[1],
        "green": p[2],
        "yellow": p[3],
        "blue": p[4],
        "magenta": p[5],
        "cyan": p[6],
        "white": p[7],
        "brightBlack": p[8],
        "brightRed": p[9],
        "brightGreen": p[10],
        "brightYellow": p[11],
        "brightBlue": p[12],
        "brightMagenta": p[13],
        "brightCyan": p[14],
        "brightWhite": p[15],
    }


def orca_data_path() -> Path:
    """Resolve the Orca per-profile settings file, overridable for tests."""
    override = os.environ.get("ORCA_DATA_PATH")
    if override:
        return Path(override)
    return Path(os.path.expanduser(_DEFAULT_DATA_PATH))


def orca_main_window_running(proc_root: Path = Path("/proc")) -> bool:
    """True while Orca's main Electron window holds orca-data.json open.

    Orca's daemon and helper processes (crashpad, session-scanner, the
    parcel watcher) stay alive after the window closes and never rewrite
    this file; only the main process does, spawned with no extra argv
    (its `--type=...` child processes are renderer/gpu/utility helpers,
    not the window that owns the write). Detecting anything less specific
    than that (e.g. any process named orca-ide) would treat those harmless
    helpers as if the window were still open and skip real sync
    opportunities for no reason.
    """
    for entry in proc_root.glob("[0-9]*/cmdline"):
        try:
            argv = entry.read_bytes().split(b"\0")
        except OSError:
            continue
        argv = [a for a in argv if a]
        if len(argv) == 1 and argv[0].decode(errors="replace").endswith("orca-ide"):
            return True
    return False


def sync_orca_theme(active: dict[str, str]) -> str:
    """Best-effort: point Orca's active terminal theme at the given palette.

    Orca keeps its own in-memory copy of orca-data.json while its main
    window is open and periodically flushes it back to disk, silently
    discarding any external edit made in that window — so this never
    writes while that window is running; it only ever updates the file
    between sessions. Returns one of "applied", "skipped-running",
    "skipped-missing" (no Orca profile on this machine), or
    "skipped-malformed" (existing file is not the expected JSON object).
    """
    if orca_main_window_running():
        return "skipped-running"

    path = orca_data_path()
    if not path.is_file():
        return "skipped-missing"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "skipped-malformed"
    if not isinstance(data, dict) or not isinstance(data.get("settings"), dict):
        return "skipped-malformed"

    theme = orca_terminal_theme(active)
    settings = data["settings"]
    existing = settings.get("terminalCustomThemes")
    themes = [t for t in existing if isinstance(t, dict)] if isinstance(existing, list) else []
    mode_key = "terminalThemeDark" if theme["name"].endswith("Dark") else "terminalThemeLight"
    already_current = settings.get(mode_key) == theme["name"] and any(
        t == theme for t in themes if t.get("name") == theme["name"]
    )
    if already_current:
        return "unchanged"

    settings["terminalCustomThemes"] = [t for t in themes if t.get("name") != theme["name"]] + [
        theme
    ]
    settings[mode_key] = theme["name"]

    tmp_path = path.with_suffix(path.suffix + ".dreamcoder-tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return "applied"
