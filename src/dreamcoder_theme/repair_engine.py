"""Safe repair planning and application."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .backups import create_backup
from .core import ROOT, active_kitty_ui, config_home
from .doctor import doctor_checks

SAFE_REPAIR_CATALOG = {
    "kitty-remove-duplicate-color-include": "Remove duplicate Kitty color include.",
    "restore-kitty-config": "Restore missing Kitty config from repo.",
    "restore-ghostty-config": "Restore missing Ghostty config from repo.",
    "restore-starship-config": "Restore missing Starship config from repo.",
    "restore-fish-config": "Restore missing Fish config from repo.",
    "restore-active-kitty-colors": "Restore active Kitty colors from repo.",
    "restore-btop-theme": "Deploy Btop theme from repo.",
    "restore-hypr-import": "Regenerate custom.lua so it loads dreamcoder-colors.",
    "restore-bat-themes": "Deploy Bat themes from repo.",
    "enable-auto-timer": "Enable dreamcoder auto-theme timer via systemctl.",
}

MANAGED_RESTORE_TARGETS = {
    "kitty config": ROOT / "DreamcoderKitty" / ".config" / "kitty",
    "ghostty config": ROOT / "DreamcoderGhostty" / ".config" / "ghostty",
    "starship config": ROOT / "DreamcoderShell" / ".config" / "starship.toml",
    "fish config": ROOT / "DreamcoderShell" / ".config" / "fish" / "config.fish",
    "btop theme": ROOT / "DreamcoderThemes" / "dreamcoder" / "btop-dreamcoder-light.theme",
    "bat theme": ROOT / "DreamcoderBat" / ".config" / "bat" / "themes" / "Dreamcoder-Dark.tmTheme",
}


def repair_catalog() -> dict[str, Any]:
    return {"schema": "dreamcoder.repair-catalog.v1", "safe_repairs": SAFE_REPAIR_CATALOG}


def safe_action(
    action_id: str,
    check: Any,
    description: str,
    source: Path | None = None,
    target: str | None = None,
) -> dict[str, Any]:
    # check.detail is a diagnostic string (sometimes a mode name, e.g.
    # "unknown"), not always a filesystem path — callers that restore a file
    # must pass an explicit absolute target.
    action = {
        "id": action_id,
        "check": check.name,
        "safe": True,
        "target": target if target is not None else check.detail,
        "description": description,
        "command": "./scripts/dreamcoder repair apply --json",
    }
    if source is not None:
        action["source"] = str(source)
    return action


def repair_plan() -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    for check in doctor_checks():
        if check.status == "ok":
            continue
        if check.name == "kitty duplicate color include":
            actions.append(
                {
                    "id": "kitty-remove-duplicate-color-include",
                    "check": check.name,
                    "safe": True,
                    "target": str(active_kitty_ui()),
                    "description": "Remove duplicate colors-dreamcoder.conf include from dreamcoder-ui.conf.",
                    "command": "./scripts/dreamcoder repair apply --json",
                }
            )
        elif check.name in {"kitty config", "ghostty config", "starship config", "fish config"}:
            source = MANAGED_RESTORE_TARGETS[check.name]
            actions.append(
                safe_action(
                    f"restore-{check.name.replace(' ', '-')}",
                    check,
                    "Restore missing managed config path from the repository.",
                    source,
                )
            )
        elif check.name == "active theme mode":
            source = ROOT / "DreamcoderKitty" / ".config" / "kitty" / "colors-dreamcoder.conf"
            actions.append(
                safe_action(
                    "restore-active-kitty-colors",
                    check,
                    "Restore active Kitty colors file from the repository.",
                    source,
                    target=str(config_home() / "kitty" / "colors-dreamcoder.conf"),
                )
            )
        elif check.name == "installer conflicts":
            actions.append(
                {
                    "id": "review-installer-conflicts",
                    "check": check.name,
                    "safe": False,
                    "target": check.detail,
                    "description": "Review conflicts before stow moves or overwrites user files.",
                    "command": "./scripts/dreamcoder installer plan --json",
                }
            )
        elif check.name == "day/night timer":
            actions.append(
                {
                    "id": "enable-day-night-timer",
                    "check": check.name,
                    "safe": False,
                    "target": "dreamcoder-theme-auto.timer",
                    "description": "Enable the user systemd timer after confirming user services are available.",
                    "command": "systemctl --user enable --now dreamcoder-theme-auto.timer",
                }
            )
        else:
            actions.append(
                {
                    "id": f"manual-{check.name.replace(' ', '-')}",
                    "check": check.name,
                    "safe": False,
                    "target": check.detail,
                    "description": "Manual review required.",
                    "command": check.repair,
                }
            )
    safe_count = sum(1 for action in actions if action["safe"])
    return {
        "schema": "dreamcoder.repair-plan.v1",
        "summary": {
            "actions": len(actions),
            "safe": safe_count,
            "manual": len(actions) - safe_count,
        },
        "catalog": repair_catalog()["safe_repairs"],
        "actions": actions,
    }


def restore_managed_path(action: dict[str, Any]) -> None:
    source = Path(action["source"])
    target = Path(action["target"])
    # Fail closed instead of dropping a stray symlink in the cwd: a repair
    # target must be an absolute path (config_home managed paths).
    if not target.is_absolute():
        raise ValueError(f"refusing to restore to non-absolute target: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        return
    target.symlink_to(source, target_is_directory=source.is_dir())


def apply_safe_repairs(dry_run: bool) -> dict[str, Any]:
    plan = repair_plan()
    safe_actions = [action for action in plan["actions"] if action["safe"]]
    result: dict[str, Any] = {
        "schema": "dreamcoder.repair-apply.v1",
        "dry_run": dry_run,
        "planned_actions": safe_actions,
        "applied_actions": [],
    }
    if dry_run or not safe_actions:
        return result

    backup_paths = [Path(action["target"]) for action in safe_actions]
    manifest = create_backup(backup_paths, "repair safe apply")
    for action in safe_actions:
        if action["id"] == "kitty-remove-duplicate-color-include":
            path = Path(action["target"])
            if path.exists():
                lines = [
                    line
                    for line in path.read_text(errors="ignore").splitlines()
                    if line.strip() != "include colors-dreamcoder.conf"
                ]
                path.write_text("\n".join(lines).rstrip() + "\n")
                result["applied_actions"].append(action)
        elif action["id"].startswith("restore-") and "source" in action:
            restore_managed_path(action)
            result["applied_actions"].append(action)
    result["backup_id"] = manifest["backup_id"]
    return result
