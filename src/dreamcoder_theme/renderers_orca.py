"""Orca theme integration, derived from the standard ANSI mapping.

Orca (an Electron-based dev IDE, unrelated to the GNOME screen reader) keeps
its own list of named terminal color schemes in its per-profile state rather
than reading a checked-in theme file, so there is no repository-variant output
here — only the settings that populate ``settings.terminalCustomThemes`` and the
surrounding theme keys.

Orca's theme ecosystem spans four coupled keys: the two terminal variants
(``terminalThemeDark``/``terminalThemeLight``), the
``terminalUseSeparateLightTheme`` switch that makes Orca look the light name
up whenever the app goes light, the per-appearance divider colors, and the
app chrome ``theme`` (forwarded to Electron's ``nativeTheme.themeSource``).
All of them must describe the same Dreamcoder mode, and both terminal
variants must exist at once: writing only the active one leaves the other
name dangling, so a light switch inside Orca falls back to its default
scheme.

A custom theme is not addressed by its display name. Orca resolves a
selection through ``parseCustomTerminalThemeSelection``: the setting must read
``custom:<id>``, and the matching entry carries the colors under a nested
``terminal`` object. Entries without usable colors are silently dropped by
``normalizeTerminalCustomThemes``, which is why a flat entry with a plain-name
selection leaves Orca on its built-in scheme while still showing the name.

Orca migrated its profile from ``orca-data.json`` to ``profile-state.db``
(SQLite). The database is authoritative whenever
``profile-state.db.authority`` says ``sqlite``; the JSON file then survives
only as an export, and editing it changes nothing Orca reads.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import time
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .palette import ansi

_DEFAULT_DATA_PATH = "~/.config/orca/profiles/local-default/orca-data.json"
_DB_NAME = "profile-state.db"
_AUTHORITY_SUFFIX = ".authority"
_SETTINGS_DOMAIN = "settings"

# Orca's own selection contract: a custom theme is selected as `custom:<id>`.
_CUSTOM_PREFIX = "custom:"
_SOURCE = "manual"
_THEME_IDS = {"dark": "manual:dreamcoder-dark", "light": "manual:dreamcoder-light"}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def orca_terminal_theme(
    c: dict[str, str], mode: str, imported_at: str | None = None
) -> dict[str, Any]:
    """Build one Orca ``terminalCustomThemes`` entry from a Dreamcoder palette."""
    if mode not in _THEME_IDS:
        raise ValueError(f"mode must be 'dark' or 'light' (got {mode!r})")
    p = ansi(c)
    terminal = {
        "foreground": c["text"],
        "background": c["bg"],
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
    return {
        "id": _THEME_IDS[mode],
        "name": c["name"],
        "source": _SOURCE,
        "mode": mode,
        "terminal": terminal,
        "importedAt": imported_at or _now_iso(),
    }


def orca_theme_settings(
    active: dict[str, str],
    variants: Mapping[str, dict[str, str]],
    mode: str,
    existing_themes: list[Any] | None = None,
) -> dict[str, Any]:
    """Build every Orca theme setting for one Dreamcoder mode.

    ``active`` is the palette of ``mode`` (already adapted to the wallpaper
    when adaptivity is on), while the other variant comes straight from
    ``variants`` so both terminal entries always stay defined. An existing
    entry with the same id keeps its original ``importedAt`` so repeated runs
    stay byte-identical instead of looking like a fresh import every time.
    """
    if mode not in {"dark", "light"}:
        raise ValueError(f"mode must be 'dark' or 'light' (got {mode!r})")
    previous: dict[str, str] = {}
    for entry in existing_themes or []:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            stamp = entry.get("importedAt")
            if isinstance(stamp, str) and stamp:
                previous[entry["id"]] = stamp
    dark = active if mode == "dark" else variants["dark"]
    light = active if mode == "light" else variants["light"]
    dark_theme = orca_terminal_theme(dark, "dark", previous.get(_THEME_IDS["dark"]))
    light_theme = orca_terminal_theme(light, "light", previous.get(_THEME_IDS["light"]))
    return {
        "terminalCustomThemes": [dark_theme, light_theme],
        "terminalThemeDark": f"{_CUSTOM_PREFIX}{dark_theme['id']}",
        "terminalThemeLight": f"{_CUSTOM_PREFIX}{light_theme['id']}",
        "terminalUseSeparateLightTheme": True,
        "theme": mode,
        "terminalDividerColorDark": dark.get("border_ui") or dark["border"],
        "terminalDividerColorLight": light.get("border_ui") or light["border"],
    }


def orca_data_path() -> Path:
    """Resolve the legacy Orca per-profile JSON file, overridable for tests."""
    override = os.environ.get("ORCA_DATA_PATH")
    if override:
        return Path(override)
    return Path(os.path.expanduser(_DEFAULT_DATA_PATH))


def orca_state_db_path() -> Path:
    """Resolve the Orca per-profile SQLite state database.

    Defaults to the sibling of the JSON path so a single override
    (``ORCA_DATA_PATH``) still points a test at its own profile directory.
    """
    override = os.environ.get("ORCA_STATE_DB_PATH")
    if override:
        return Path(override)
    return orca_data_path().parent / _DB_NAME


def _orca_authority(db_path: Path) -> str:
    """Read the store Orca considers authoritative ('sqlite' or '')."""
    try:
        return (
            db_path.with_name(db_path.name + _AUTHORITY_SUFFIX)
            .read_text(encoding="utf-8")
            .strip()
            .lower()
        )
    except OSError:
        return ""


def orca_store() -> tuple[str, Path]:
    """Return the store Orca actually reads: ("sqlite"|"json"|"missing", path)."""
    db_path = orca_state_db_path()
    if db_path.is_file() and _orca_authority(db_path) == "sqlite":
        return "sqlite", db_path
    data_path = orca_data_path()
    if data_path.is_file():
        return "json", data_path
    if db_path.is_file():
        return "sqlite", db_path
    return "missing", data_path


def orca_main_window_running(proc_root: Path = Path("/proc")) -> bool:
    """True while Orca's main Electron window holds its profile open.

    Orca's daemon and helper processes (crashpad, session-scanner, the
    parcel watcher) stay alive after the window closes and never rewrite
    the profile; only the main process does, spawned with no extra argv
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


def _read_json_settings(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("settings"), dict):
        return None
    return data


def _read_sqlite_settings(db_path: Path) -> tuple[dict[str, Any], int] | None:
    """Return (settings, profile revision) from the authoritative database."""
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        row = conn.execute(
            "SELECT payload FROM profile_state_documents WHERE domain = ?",
            (_SETTINGS_DOMAIN,),
        ).fetchone()
        meta = conn.execute(
            "SELECT value FROM profile_state_meta WHERE key = 'revision'"
        ).fetchone()
    except sqlite3.Error:
        return None
    finally:
        conn.close()
    if row is None or meta is None:
        return None
    try:
        settings = json.loads(row[0])
        revision = int(meta[0])
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(settings, dict):
        return None
    return settings, revision


def _backup_sqlite(db_path: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.dreamcoder-backup.{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def _write_sqlite_settings(db_path: Path, settings: dict[str, Any]) -> None:
    """Persist settings the way Orca's own document store does.

    A domain row records the profile revision at which it was last written
    and ``content_hash`` is the sha256 of the exact payload bytes; the profile
    revision in ``profile_state_meta`` moves to the new value. Writing any
    other shape trips Orca's "document revision exceeds profile revision"
    check and lands the profile in recovery.
    """
    read = _read_sqlite_settings(db_path)
    if read is None:
        raise RuntimeError("cannot read the Orca settings document")
    _, revision = read
    payload = json.dumps(settings, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    new_revision = revision + 1
    _backup_sqlite(db_path)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE profile_state_documents"
                " SET payload = ?, revision = ?, updated_at = ?, content_hash = ?"
                " WHERE domain = ?",
                (
                    payload,
                    new_revision,
                    int(time.time() * 1000),
                    digest,
                    _SETTINGS_DOMAIN,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("Orca settings document is missing")
            conn.execute(
                "UPDATE profile_state_meta SET value = ? WHERE key = 'revision'",
                (str(new_revision),),
            )
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def _write_json_settings(path: Path, data: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".dreamcoder-tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def _load_profile(store: str, path: Path) -> tuple[dict[str, Any], dict[str, Any] | None] | None:
    """Return ``(settings, json_wrapper)`` for the active store.

    ``json_wrapper`` is the whole document when the store is the legacy JSON
    file, and ``None`` for SQLite. Returns ``None`` when the profile is not the
    expected shape.
    """
    if store == "sqlite":
        read = _read_sqlite_settings(path)
        if read is None:
            return None
        return read[0], None
    data = _read_json_settings(path)
    if data is None:
        return None
    return data["settings"], data


def _save_profile(
    store: str,
    path: Path,
    settings: dict[str, Any],
    wrapper: dict[str, Any] | None,
) -> None:
    """Persist ``settings`` back into the active store."""
    if store == "sqlite":
        _write_sqlite_settings(path, settings)
        return
    if wrapper is None:
        raise ValueError("JSON profile document is missing")
    wrapper["settings"] = settings
    _write_json_settings(path, wrapper)


def sync_orca_theme(
    active: dict[str, str],
    variants: Mapping[str, dict[str, str]],
    mode: str,
) -> str:
    """Best-effort: point every Orca theme key at the given Dreamcoder mode.

    Orca keeps its own in-memory copy of the profile while its main window is
    open and periodically flushes it back to disk, silently discarding any
    external edit made in that window — so this never writes while that window
    is running; it only ever updates the profile between sessions. Every run
    rewrites both terminal entries, which also repairs a profile whose theme
    names survived while their definitions were dropped. Returns one of
    "applied", "unchanged", "skipped-running", "skipped-missing" (no Orca
    profile on this machine), or "skipped-malformed" (the existing profile is
    not the expected shape).
    """
    if orca_main_window_running():
        return "skipped-running"

    store, path = orca_store()
    if store == "missing":
        return "skipped-missing"

    loaded = _load_profile(store, path)
    if loaded is None:
        return "skipped-malformed"
    settings, wrapper = loaded

    existing = settings.get("terminalCustomThemes")
    existing_themes = (
        [t for t in existing if isinstance(t, dict)] if isinstance(existing, list) else []
    )
    desired = orca_theme_settings(active, variants, mode, existing_themes)
    managed_ids = {t["id"] for t in desired["terminalCustomThemes"]}
    managed_names = {t["name"] for t in desired["terminalCustomThemes"]}
    # Drop both the current id-addressed entries and the older flat, name-only
    # shape a previous Dreamcoder version wrote, which Orca itself discards.
    merged = [
        t
        for t in existing_themes
        if t.get("id") not in managed_ids and t.get("name") not in managed_names
    ] + list(desired["terminalCustomThemes"])

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
    _save_profile(store, path, settings, wrapper)
    return "applied"
