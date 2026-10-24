"""Orca theme integration, derived from the standard ANSI mapping.

Orca (an Electron-based dev IDE, unrelated to the GNOME screen reader) keeps
its own list of named terminal color schemes in its per-profile settings
file rather than reading a checked-in theme file, so there is no
repository-variant output here — only the settings that populate
``settings.terminalCustomThemes`` and the surrounding theme keys in that file.

Orca's theme ecosystem spans four coupled keys: the two terminal variants
(``terminalThemeDark``/``terminalThemeLight``), the
``terminalUseSeparateLightTheme`` switch that makes Orca look the light name
up whenever the app goes light, the per-appearance divider colors, and the
app chrome ``theme`` (forwarded to Electron's ``nativeTheme.themeSource``).
All of them must describe the same Dreamcoder mode, and both terminal
variants must exist at once: writing only the active one leaves the other
name dangling, so a light switch inside Orca falls back to its default
scheme.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

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


def orca_theme_settings(
    active: dict[str, str],
    variants: Mapping[str, dict[str, str]],
    mode: str,
) -> dict[str, Any]:
    """Build every Orca theme setting for one Dreamcoder mode.

    ``active`` is the palette of ``mode`` (already adapted to the wallpaper
    when adaptivity is on), while the other variant comes straight from
    ``variants`` so both terminal entries always stay defined.
    """
    if mode not in {"dark", "light"}:
        raise ValueError(f"mode must be 'dark' or 'light' (got {mode!r})")
    dark = active if mode == "dark" else variants["dark"]
    light = active if mode == "light" else variants["light"]
    dark_theme = orca_terminal_theme(dark)
    light_theme = orca_terminal_theme(light)
    return {
        "terminalCustomThemes": [dark_theme, light_theme],
        "terminalThemeDark": dark_theme["name"],
        "terminalThemeLight": light_theme["name"],
        "terminalUseSeparateLightTheme": True,
        "theme": mode,
        "terminalDividerColorDark": dark.get("border_ui") or dark["border"],
        "terminalDividerColorLight": light.get("border_ui") or light["border"],
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


def sync_orca_theme(
    active: dict[str, str],
    variants: Mapping[str, dict[str, str]],
    mode: str,
) -> str:
    """Best-effort: point every Orca theme key at the given Dreamcoder mode.

    Orca keeps its own in-memory copy of orca-data.json while its main
    window is open and periodically flushes it back to disk, silently
    discarding any external edit made in that window — so this never
    writes while that window is running; it only ever updates the file
    between sessions. Every run rewrites both terminal entries, which also
    repairs a file whose theme names survived while their definitions were
    dropped. Returns one of "applied", "unchanged", "skipped-running",
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

    desired = orca_theme_settings(active, variants, mode)
    settings = data["settings"]
    existing = settings.get("terminalCustomThemes")
    existing_themes = (
        [t for t in existing if isinstance(t, dict)] if isinstance(existing, list) else []
    )
    managed = {t["name"] for t in desired["terminalCustomThemes"]}
    merged = [t for t in existing_themes if t.get("name") not in managed] + list(
        desired["terminalCustomThemes"]
    )

    changed = merged != existing_themes
    for key, value in desired.items():
        if key == "terminalCustomThemes":
            continue
        if settings.get(key) != value:
            settings[key] = value
            changed = True
    if not changed:
        return "unchanged"

    settings["terminalCustomThemes"] = merged

    tmp_path = path.with_suffix(path.suffix + ".dreamcoder-tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    return "applied"
