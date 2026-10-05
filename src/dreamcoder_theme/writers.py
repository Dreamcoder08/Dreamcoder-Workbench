"""Filesystem writers and app config updaters."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _ensure_single_trailing_newline(content: str) -> str:
    """Normalize to end with exactly one newline (POSIX text files).

    Matches the repo's end-of-file-fixer hook so generated output commits
    cleanly instead of being re-fixed at every commit.
    """
    if not content:
        return content
    return content.rstrip() + "\n"


def write_if_changed(path: Path, content: str, *, replace_symlink: bool = False) -> bool:
    content = _ensure_single_trailing_newline(content)
    old = path.read_text() if path.exists() else ""
    if old == content and not (replace_symlink and path.is_symlink()):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if replace_symlink:
        # Replace the directory entry, never the repository variant behind a link.
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        try:
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    else:
        path.write_text(content)
    return True


def write_opencode_tui(path: Path) -> bool:
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            data = {}
    data["$schema"] = data.get("$schema", "https://opencode.ai/tui.json")
    data["theme"] = "dreamcoder"
    return write_if_changed(path, json.dumps(data, indent=2) + "\n")


def cleanup_opencode_themes(path: Path) -> bool:
    changed = False
    keep = path.name
    if os.environ.get("DREAMCODER_CLEAN_OPENCODE_THEMES", "1") == "0":
        return False
    for theme in path.parent.glob("*.json"):
        if theme.name != keep:
            theme.unlink()
            changed = True
    return changed


def ensure_codex_theme_config(path: Path) -> bool:
    theme_line = 'theme = "Dreamcoder"'
    if not path.exists():
        return write_if_changed(path, f"[tui]\n{theme_line}\n")
    content = path.read_text()
    if re.search(r"(?m)^\s*theme\s*=", content) and "[tui]" in content:
        return False
    if "[tui]" in content:
        updated = re.sub(r"(?m)^\[tui\]\s*$", f"[tui]\n{theme_line}", content, count=1)
    else:
        updated = content.rstrip() + f"\n\n[tui]\n{theme_line}\n"
    return write_if_changed(path, updated)


def ensure_pi_theme_settings(path: Path) -> bool:
    data: dict[str, Any] = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            data = {}
    if data.get("theme") == "dreamcoder":
        return False
    data["theme"] = "dreamcoder"
    return write_if_changed(path, json.dumps(data, indent=2) + "\n", replace_symlink=True)


def valid_starship(path: Path) -> bool:
    if not shutil.which("starship"):
        return True
    return (
        subprocess.run(
            ["starship", "explain"],
            env={**os.environ, "STARSHIP_CONFIG": str(path)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        ).returncode
        == 0
    )


def ensure_kitty_ui_include(path: Path) -> bool:
    line = "include dreamcoder-ui.conf"
    if not path.exists():
        return False
    content = path.read_text()
    if line in content:
        return False
    path.write_text(content.rstrip() + "\n\n# Dreamcoder readability override\n" + line + "\n")
    return True


def update_ghostty_theme(path: Path, mode: str) -> bool:
    """Update Ghostty config to use the correct theme name, opacity, and blur.

    The legacy ``dreamcoder`` name is retained only for light; dark keeps
    ``dreamcoder-dark``.
    """
    if not path.exists():
        return False
    content = path.read_text()
    theme_name = "dreamcoder-dark" if mode != "light" else "dreamcoder"

    changed = False

    # Theme line only — opacity/blur are now set in the .ghostty theme file
    # via ghostty_content() so they stay consistent with the palette.
    if re.search(rf"theme\s*=\s*{re.escape(theme_name)}(?:\s|$)", content):
        pass  # already correct
    elif re.search(r"theme\s*=", content):
        content = re.sub(r"theme\s*=.*", f"theme = {theme_name}", content)
        changed = True
    else:
        content = content.rstrip() + f"\n\n# Theme\ntheme = {theme_name}\n"
        changed = True

    return write_if_changed(path, content) if changed else False


def update_zellij_config(path: Path, mode: str) -> bool:
    """Patch Zellij config.kdl to select ``theme "dreamcoder-{mode}"``."""
    if not path.exists():
        return False
    content = path.read_text()
    theme_name = f"dreamcoder-{mode}"

    new_line = f'theme "{theme_name}"'
    pattern = re.compile(r'^\s*theme\s+".*?"\s*$', re.MULTILINE)
    m = pattern.search(content)
    if m and m.group().strip() == f'theme "{theme_name}"':
        return False
    if m:
        content = pattern.sub(new_line, content, count=1)
    else:
        content = content.rstrip() + "\n" + new_line + "\n"
    return write_if_changed(path, content)


def update_warp_settings(path: Path, mode: str) -> bool:
    """Patch owned Warp opacity/blur keys without replacing personal settings.

    Dark opacity covers the whole canvas; retained blur does not add region glass.
    Missing files are created. False means a verified successful no-op; rejected
    documents raise ValueError before writing so activation can roll back.
    """
    if mode == "dark":
        opacity_val = 100
        blur_val = 20
        blur_texture = True
    else:
        opacity_val = 96
        blur_val = 1
        blur_texture = False

    section_header = "[appearance.window]"
    expected = (
        f"{section_header}\n"
        f"override_opacity = {opacity_val}\n"
        f"override_blur = {blur_val}\n"
        f"override_blur_texture = {str(blur_texture).lower()}\n"
    )

    content = path.read_text() if path.exists() else ""
    try:
        intended = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Warp settings rejected: {path}: invalid TOML; file unchanged") from exc
    appearance = intended.setdefault("appearance", {})
    if not isinstance(appearance, dict):
        raise ValueError(
            f"Warp settings rejected: {path}: appearance is not a table; file unchanged"
        )
    window_exists = "window" in appearance
    window = appearance.setdefault("window", {})
    if not isinstance(window, dict):
        raise ValueError(
            f"Warp settings rejected: {path}: appearance.window is not a table; file unchanged"
        )
    window.update(
        override_opacity=opacity_val,
        override_blur=blur_val,
        override_blur_texture=blur_texture,
    )

    patched = _patch_warp_window(content, expected, window_exists, window)
    if patched is None:
        raise ValueError(
            f"Warp settings rejected: {path}: unsupported appearance.window layout; file unchanged"
        )

    # Regexes locate a conservative text patch, not a TOML parser. Reject false
    # matches inside multiline strings, duplicates, or any unrelated semantic edit.
    try:
        verified = tomllib.loads(patched)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(
            f"Warp settings rejected: {path}: patch would produce invalid TOML; file unchanged"
        ) from exc
    if verified != intended:
        raise ValueError(
            f"Warp settings rejected: {path}: patch would alter unrelated settings; file unchanged"
        )
    return write_if_changed(path, patched)


def _patch_warp_window(
    content: str, expected: str, window_exists: bool, window: dict[str, Any]
) -> str | None:
    """Locate only Warp's explicit window table; leave unsupported layouts alone."""
    if content:
        # Horizontal whitespace only: include indented regular/array table boundaries.
        sec_re = re.compile(
            r"^[ \t]*\[(?:appearance|\"appearance\"|'appearance')[ \t]*\.[ \t]*"
            r"(?:window|\"window\"|'window')\][^\n]*\n?.*?(?=^[ \t]*\[|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        existing_section = sec_re.search(content)
        if existing_section:
            section = existing_section.group()
            for key, value in (
                ("override_opacity", str(window["override_opacity"])),
                ("override_blur", str(window["override_blur"])),
                ("override_blur_texture", str(window["override_blur_texture"]).lower()),
            ):
                pattern = re.compile(
                    rf"^([ \t]*(?:{key}|\"{key}\"|'{key}')[ \t]*=[ \t]*)[^\s#]+",
                    re.MULTILINE,
                )
                if pattern.search(section):
                    section = pattern.sub(lambda m: m.group(1) + value, section)
                else:
                    section += ("" if section.endswith("\n") else "\n") + f"{key} = {value}\n"
            patched = (
                content[: existing_section.start()] + section + content[existing_section.end() :]
            )
        else:
            if window_exists:
                return None  # Inline/dotted or unsupported quoted table: preserve it.
            patched = content + ("\n" if content.endswith("\n") else "\n\n") + expected
    else:
        patched = expected

    return patched


def write_variant_files(
    base: Path,
    names: dict[str, str],
    builder: Callable[..., str],
    variants: dict[str, dict[str, str]],
) -> list[bool]:
    """Write every named variant, failing closed before the first write.

    The declared ``names`` must be a subset of the provided ``variants`` map
    (dark/light) so a caller can never silently fall back to another palette
    for a missing variant: the preflight raises before any file is touched.
    """
    missing = set(names) - set(variants)
    if missing:
        raise ValueError(
            f"variant names {sorted(missing)} missing from variants map; "
            "aborting before any write (no silent standard-dark fallback)"
        )
    return [
        write_if_changed(base / file_name, builder(variants[mode_name]))
        for mode_name, file_name in names.items()
    ]


def write_variant_files_and_active(
    base: Path,
    names: dict[str, str],
    builder: Callable[..., str],
    variants: dict[str, dict[str, str]],
    active: dict[str, str],
    active_path: Path,
) -> list[bool]:
    """Prepared variant + active writes for one activation transaction (design §6).

    All content is rendered in memory before the first write, and
    ``write_variant_files``' fail-closed ``names <= variants`` preflight runs
    before any file is touched — a missing variant or a render error
    aborts with zero mutations. Full snapshot/rollback of the activation
    transaction is owned by the Phase 5 activation layer.
    """
    active_content = builder(active)
    changes = write_variant_files(base, names, builder, variants)
    changes.append(write_if_changed(active_path, active_content))
    return changes
