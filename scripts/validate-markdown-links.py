#!/usr/bin/env python3
"""Validate relative markdown links in the repository.

Skips external URLs, mailto, anchor-only, absolute, and archived-tree links;
checks relative file targets and best-effort #anchors.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories skipped anywhere in the tree (vendored, generated, or local).
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    ".local-backups",
    "logs",
    ".firecrawl",
    ".codegraph",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".coverage",
    ".superpowers",
    ".opencode",
    ".tmp",
    ".claude",
    ".gemini",
    ".pi",
    ".pi-subagents",
    "info",
    "ml4w_assets",
    "lib",
    ".egg-info",
}

# Historical / machine-generated trees known to contain stale links.
ARCHIVED = (ROOT / "docs" / "superpowers", ROOT / "docs" / "generated")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+[^)]*)\)")
SLUG_RE = re.compile(r"[^a-z0-9\- ]")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def in_scope(path: Path, include_archived: bool) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return include_archived or not any(path == base or base in path.parents for base in ARCHIVED)


def iter_markdown(paths: list[Path], include_archived: bool) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        found = sorted(path.rglob("*.md")) if path.is_dir() else [path]
        files.extend(p for p in found if p.suffix == ".md" and in_scope(p, include_archived))
    return files


def slugify(text: str) -> str:
    text = SLUG_RE.sub("", text.strip().lower())
    return re.sub(r" +", "-", text).strip("-")


def is_skippable(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "/", "#")) or (
        target.startswith("<") and target.endswith(">")
    )


def check_file(path: Path) -> list[str]:
    broken: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return broken
    headings: set[str] | None = None
    in_fence = False
    for lineno, line in enumerate(lines, 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            for raw_target in LINK_RE.findall(INLINE_CODE_RE.sub("", line)):
                target = raw_target.strip()
                if not target or is_skippable(target):
                    continue
                file_part, _, anchor = target.partition("#")
                resolved = path.parent / file_part
                if not resolved.exists():
                    broken.append(f"{path}:{lineno}: {target}")
                    continue
                if anchor and resolved.is_file():
                    if headings is None:
                        headings = {slugify(h.lstrip("# ")) for h in lines if h.startswith("#")}
                    if slugify(anchor) not in headings:
                        broken.append(f"{path}:{lineno}: {target}")
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate relative markdown links in the repository."
    )
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="also check docs/superpowers/ and docs/generated/",
    )
    parser.add_argument(
        "paths", nargs="*", help="files or directories to check (default: whole repo)"
    )
    args = parser.parse_args(argv)
    bases = [Path(p).resolve() for p in args.paths] or [ROOT]
    broken: list[str] = []
    for path in iter_markdown(bases, args.include_archived):
        broken.extend(check_file(path))
    for entry in sorted(broken):
        print(entry)
    if broken:
        print(f"{len(broken)} broken link(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
