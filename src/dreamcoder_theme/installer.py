"""Installer target planning and conflict classification."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .core import ROOT, config_home, data_home


def managed_targets() -> list[dict[str, Any]]:
    ch = config_home()
    dh = data_home()
    home = Path.home()
    return [
        {"module": "DreamcoderKitty", "path": str(ch / "kitty")},
        {"module": "DreamcoderGhostty", "path": str(ch / "ghostty")},
        {"module": "DreamcoderFastfetch", "path": str(ch / "fastfetch")},
        {"module": "DreamcoderFastfetch", "path": str(ch / "dreamcoder")},
        {"module": "DreamcoderShell", "path": str(ch / "fish")},
        {"module": "DreamcoderShell", "path": str(ch / "starship.toml")},
        {"module": "DreamcoderShell", "path": str(home / ".zshrc")},
        {"module": "DreamcoderShell", "path": str(home / ".bashrc")},
        {"module": "DreamcoderShell", "path": str(home / ".inputrc")},
        {"module": "DreamcoderBat", "path": str(ch / "bat")},
        {"module": "DreamcoderWarp", "path": str(dh / "warp-terminal" / "themes")},
        {
            "module": "DreamcoderSystemd",
            "path": str(ch / "systemd" / "user" / "dreamcoder-theme-auto.service"),
        },
        {
            "module": "DreamcoderSystemd",
            "path": str(ch / "systemd" / "user" / "dreamcoder-theme-auto.timer"),
        },
    ]


def classify_target(path: Path) -> tuple[str, str]:
    if not path.exists() and not path.is_symlink():
        return "missing", "target does not exist yet"
    if path.is_symlink():
        try:
            resolved = path.resolve(strict=False)
        except OSError:
            resolved = Path(os.readlink(path))
        try:
            resolved.relative_to(ROOT)
            return "managed", f"symlink managed by repo: {resolved}"
        except ValueError:
            return "conflict", f"external symlink: {resolved}"
    if path.is_dir():
        children = list(path.iterdir())
        if children and all(child.is_symlink() for child in children):
            external = []
            for child in children:
                try:
                    child.resolve(strict=False).relative_to(ROOT)
                except ValueError:
                    external.append(child)
            if not external:
                return "managed", "directory contains only repo-managed symlinks"
    return "conflict", "existing non-symlink target requires backup/move before stow"


def installer_plan() -> dict[str, Any]:
    targets = []
    conflicts = []
    for item in managed_targets():
        path = Path(item["path"])
        status, detail = classify_target(path)
        row = {**item, "status": status, "detail": detail}
        targets.append(row)
        if status == "conflict":
            conflicts.append(row)
    target_args = " ".join(json.dumps(item["path"]) for item in targets)
    return {
        "schema": "dreamcoder.install-plan.v1",
        "modules": [
            "DreamcoderShell",
            "DreamcoderKitty",
            "DreamcoderGhostty",
            "DreamcoderFastfetch",
            "DreamcoderWarp",
            "DreamcoderBat",
            "DreamcoderSystemd",
        ],
        "targets": targets,
        "conflicts": conflicts,
        "backup_command": f"./scripts/dreamcoder backup create {target_args} --reason install-preflight --json",
        "stow_command": "stow -t ${HOME} DreamcoderShell DreamcoderKitty DreamcoderGhostty DreamcoderFastfetch DreamcoderWarp DreamcoderBat DreamcoderSystemd",
    }
