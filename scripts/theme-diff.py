#!/usr/bin/env python3
"""Perceptual regression report between two versions of tokens.json.

Compares every semantic colour role (`modes.<mode>.<role>`, hex values) of a
base against the head and prints, per changed role, the CIEDE2000 difference
(ΔE) and the WCAG and APCA contrast against `bg`. A role at or above ΔE 2 is
marked `≥2`: that is about the just-noticeable difference of a side-by-side
pair. A contrast floor is *crossed* when a foreground/background pair met its
floor in the base and misses it in the head; a floor that already failed in the
base is never reported. Floors come from the head's `guardrails`.

The base is a git REF (default origin/main) read from `--repo`, or a file given
with `--base-file`. The head is the working tree file, or `--head-file`.
Reads files and runs `git show` only; writes nothing.

Exit codes: 0 report printed (informative), 1 a floor was crossed and
`--fail-on-floor` was given, 2 usage or input error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme._math import apca_lc, contrast  # noqa: E402
from dreamcoder_theme.color_space import delta_e2000  # noqa: E402

TOKENS_RELATIVE = "DreamcoderThemes/dreamcoder/tokens.json"
VISIBLE_DELTA_E = 2.0
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

TEXT_ROLES = (
    "text",
    "text_heading",
    "muted",
    "accent",
    "accent_2",
    "diagnostic",
    "sage",
    "success",
    "info",
    "lavender",
    "mauve",
    "error",
    "warning",
    "link",
)
QUIET_ROLES = ("comment", "subtle")
UI_ROLES = ("border_ui", "focus")
SURFACES = ("bg", "surface0", "surface1", "surface2")
PAIRED_FILLS = (("on_accent", "accent"), ("on_error", "error"), ("on_focus", "focus"))

Floor = tuple[str, str, str, float]  # (foreground role, background role, metric, minimum)


class InputError(Exception):
    """The base or head tokens could not be read."""


def _load(text: str, label: str) -> dict[str, Any]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise InputError(f"{label}: not valid JSON: {error}") from error
    if not isinstance(document, dict) or not isinstance(document.get("modes"), dict):
        raise InputError(f"{label}: no `modes` object")
    return document


def _read_file(path: Path) -> dict[str, Any]:
    try:
        return _load(path.read_text(encoding="utf-8"), str(path))
    except OSError as error:
        raise InputError(f"{path}: {error.strerror or error}") from error


def _read_ref(repo: Path, ref: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{TOKENS_RELATIVE}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        raise InputError(f"cannot read {TOKENS_RELATIVE} at {ref}: {detail[0] if detail else ''}")
    return _load(result.stdout, f"{ref}:{TOKENS_RELATIVE}")


def _colors(mode: dict[str, Any]) -> dict[str, str]:
    return {k: v.lower() for k, v in mode.items() if isinstance(v, str) and HEX.match(v)}


def _floors(guardrails: dict[str, Any], mode: str) -> list[Floor]:
    dark = mode == "dark"
    text = float(guardrails.get("minimum_text_contrast", 4.5))
    body = float(guardrails.get("minimum_apca_body_dark" if dark else "minimum_apca_body", 75))
    quiet = float(guardrails.get("minimum_apca_quiet", 44))
    ui = float(guardrails.get("minimum_apca_ui_dark" if dark else "minimum_apca_ui", 60))
    on_accent = float(guardrails.get("minimum_apca_on_accent", 60))
    selection = float(guardrails.get("minimum_terminal_selection_contrast", 7.0))
    floors: list[Floor] = []
    for surface in SURFACES:
        for role in TEXT_ROLES:
            floors += [(role, surface, "WCAG", text), (role, surface, "APCA", body)]
        for role in QUIET_ROLES:
            floors += [(role, surface, "WCAG", text), (role, surface, "APCA", quiet)]
    for role in UI_ROLES:
        floors += [(role, "bg", "WCAG", 3.0), (role, "bg", "APCA", ui)]
    for fg, fill in PAIRED_FILLS:
        floors += [(fg, fill, "WCAG", text), (fg, fill, "APCA", on_accent)]
    floors.append(("selection_fg", "selection_bg", "WCAG", selection))
    return floors


def _measure(metric: str, fg: str, bg: str) -> float:
    return contrast(fg, bg) if metric == "WCAG" else abs(apca_lc(fg, bg))


def _fmt(metric: str, value: float) -> str:
    return f"{value:.2f}" if metric == "WCAG" else f"{value:.1f}"


def _contrast_note(base: dict[str, str], head: dict[str, str], role: str) -> str:
    if role == "bg" or "bg" not in base or "bg" not in head:
        return ""
    parts = [
        f"{metric} {_fmt(metric, _measure(metric, base[role], base['bg']))}"
        f" -> {_fmt(metric, _measure(metric, head[role], head['bg']))}"
        for metric in ("WCAG", "APCA")
    ]
    return "  " + "  ".join(parts) + " on bg"


def _compare(
    mode: str, base: dict[str, str], head: dict[str, str], guardrails: dict[str, Any]
) -> tuple[list[tuple[float, str, str]], list[str], list[str], int]:
    """(ΔE, role, line) per changed role, FLOOR lines, RECOVERED lines, roles compared."""
    shared = [role for role in head if role in base]
    changed: list[tuple[float, str, str]] = []
    for role in shared:
        if base[role] == head[role]:
            continue
        delta = delta_e2000(base[role], head[role])
        mark = "  ≥2 (visible)" if delta >= VISIBLE_DELTA_E else ""
        line = (
            f"{mode}.{role}  {base[role]} -> {head[role]}  ΔE {delta:.2f}{mark}"
            f"{_contrast_note(base, head, role)}"
        )
        changed.append((delta, f"{mode}.{role}", line))

    crossed: list[str] = []
    recovered: list[str] = []
    for fg, bg, metric, minimum in _floors(guardrails, mode):
        if not all(role in base and role in head for role in (fg, bg)):
            continue
        before = _measure(metric, base[fg], base[bg])
        after = _measure(metric, head[fg], head[bg])
        detail = (
            f"{mode}.{fg} on {bg}: {metric} {_fmt(metric, before)} -> {_fmt(metric, after)} "
            f"(floor {_fmt(metric, minimum)})"
        )
        if before >= minimum > after:
            crossed.append(f"FLOOR {detail}")
        elif after >= minimum > before:
            recovered.append(f"RECOVERED {detail}")
    return changed, crossed, recovered, len(shared)


def build_report(
    base: dict[str, Any], head: dict[str, Any], base_label: str, head_label: str
) -> tuple[list[str], int]:
    """(report lines, crossed-floor count)."""
    guardrails: dict[str, Any] = head.get("guardrails", {})
    changed: list[tuple[float, str, str]] = []
    crossed: list[str] = []
    recovered: list[str] = []
    notes: list[str] = []
    compared = 0
    for mode, head_mode in head["modes"].items():
        base_mode = base["modes"].get(mode)
        if not isinstance(head_mode, dict) or not isinstance(base_mode, dict):
            continue
        base_colors, head_colors = _colors(base_mode), _colors(head_mode)
        mode_changed, mode_crossed, mode_recovered, count = _compare(
            mode, base_colors, head_colors, guardrails
        )
        changed += mode_changed
        crossed += mode_crossed
        recovered += mode_recovered
        compared += count
        added = [r for r in head_colors if r not in base_colors]
        removed = [r for r in base_colors if r not in head_colors]
        if added:
            notes.append(f"note: {mode} roles only in head: {', '.join(added)}")
        if removed:
            notes.append(f"note: {mode} roles only in base: {', '.join(removed)}")

    header = f"theme-diff: base {base_label} -> head {head_label}"
    if not changed:
        return [f"theme-diff: no perceptual change ({compared} roles compared)", *notes], 0

    changed.sort(key=lambda item: (-item[0], item[1]))
    visible = sum(1 for delta, _, _ in changed if delta >= VISIBLE_DELTA_E)
    top, bottom = changed[0], changed[-1]
    summary = (
        f"summary: {len(changed)} of {compared} roles changed, {visible} at or above ΔE 2, "
        f"max ΔE {top[0]:.2f} ({top[1]}), min ΔE {bottom[0]:.2f} ({bottom[1]}), "
        f"floors crossed: {len(crossed)}"
    )
    lines = [header, *(line for _, _, line in changed), *crossed, *recovered, *notes, summary]
    return lines, len(crossed)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Perceptual (ΔE2000) and contrast-floor diff of tokens.json against a base."
    )
    parser.add_argument(
        "ref", metavar="REF", nargs="?", help="git ref of the base (default: origin/main)"
    )
    parser.add_argument(
        "--base-file", type=Path, help="tokens file used as the base, instead of REF"
    )
    parser.add_argument(
        "--head-file", type=Path, help="tokens file used as the head (default: working tree)"
    )
    parser.add_argument("--repo", type=Path, default=ROOT, help="repository holding REF and tokens")
    parser.add_argument(
        "--fail-on-floor", action="store_true", help="exit 1 when a contrast floor is crossed"
    )
    args = parser.parse_args(argv)
    if args.base_file is not None and args.ref is not None:
        parser.error("give either REF or --base-file, not both")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        head_path = args.head_file or args.repo / TOKENS_RELATIVE
        head = _read_file(head_path)
        if args.base_file is not None:
            base, base_label = _read_file(args.base_file), args.base_file.name
        else:
            ref = args.ref or "origin/main"
            base, base_label = _read_ref(args.repo, ref), ref
    except InputError as error:
        print(f"theme-diff: {error}", file=sys.stderr)
        return 2
    head_label = head_path.name if args.head_file else "working tree"
    lines, crossed = build_report(base, head, base_label, head_label)
    print("\n".join(lines))
    return 1 if crossed and args.fail_on_floor else 0


if __name__ == "__main__":
    raise SystemExit(main())
