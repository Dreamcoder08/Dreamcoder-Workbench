"""CLI command handlers for Dreamcoder Control Center."""

from __future__ import annotations

import argparse
import contextlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from dreamcoder_theme import sync
from dreamcoder_theme.audit import audit_markdown, audit_report
from dreamcoder_theme.backups import create_backup, list_backups, restore_backup
from dreamcoder_theme.core import (
    ROOT,
    active_ghostty_config,
    active_hyprland_conf,
    active_hyprland_input_lua,
    active_kitty_ui,
    active_motion_path,
    active_profile_path,
    emit,
    settings_path,
    write_json,
)
from dreamcoder_theme.dashboard import dashboard_markdown, dashboard_report
from dreamcoder_theme.docs_report import docs_markdown, docs_report, write_docs_report
from dreamcoder_theme.installer import installer_plan
from dreamcoder_theme.motion import MOTION_PRESETS, apply_motion_files
from dreamcoder_theme.profiles import apply_profile_files, load_profiles, profile_changes
from dreamcoder_theme.repair_engine import apply_safe_repairs, repair_catalog, repair_plan
from dreamcoder_theme.settings import theme_paths, write_repo_enabled
from dreamcoder_theme.settings_store import (
    set_nested_setting,
    settings_get,
    settings_schema,
    settings_set,
    validate_settings,
)
from dreamcoder_theme.tui import tui_apply_setting, tui_model, tui_render
from dreamcoder_theme.visual_regression import (
    visual_audit,
    visual_audit_markdown,
    visual_markdown,
    visual_plan,
)
from dreamcoder_theme.writers import valid_starship


def handle_dashboard(args: argparse.Namespace) -> int:
    report = dashboard_report()
    if args.markdown:
        print(dashboard_markdown(report), end="")
        return 0
    emit(report, args.json)
    return 0


def handle_repair(args: argparse.Namespace) -> int:
    if args.repair_cmd == "catalog":
        emit(repair_catalog(), args.json)
        return 0
    if args.repair_cmd == "plan":
        emit(repair_plan(), args.json)
        return 0
    if args.repair_cmd == "apply":
        emit(apply_safe_repairs(args.dry_run), args.json)
        return 0
    return 2


def handle_tui(args: argparse.Namespace) -> int:
    if args.tui_cmd == "render":
        model = tui_model()
        if args.json:
            emit(model, True)
        else:
            print(tui_render(model), end="")
        return 0
    if args.tui_cmd == "set":
        try:
            result = tui_apply_setting(args.key, args.value, args.dry_run)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        emit(result, args.json)
        return 0
    return 2


def handle_docs(args: argparse.Namespace) -> int:
    if args.docs_cmd == "report":
        report = docs_report()
        if args.write:
            emit(write_docs_report(), args.json)
        elif args.markdown:
            print(docs_markdown(report), end="")
        else:
            emit(report, args.json)
        return 0
    return 2


def handle_audit(args: argparse.Namespace) -> int:
    if args.audit_cmd == "compare":
        report = audit_report()
        if args.markdown:
            print(audit_markdown(report), end="")
        else:
            emit(report, args.json)
        return 0
    return 2


def handle_visual(args: argparse.Namespace) -> int:
    if args.visual_cmd == "plan":
        report = visual_plan()
        if args.markdown:
            print(visual_markdown(report), end="")
        else:
            emit(report, args.json)
        return 0
    if args.visual_cmd == "audit":
        report = visual_audit()
        if args.markdown:
            print(visual_audit_markdown(report), end="")
        else:
            emit(report, args.json)
        return 0
    return 2


def handle_profile(args: argparse.Namespace) -> int:
    profiles = load_profiles()
    if args.profile_cmd == "list":
        emit({"profiles": profiles}, args.json)
        return 0
    if args.name not in profiles:
        print(f"Unknown profile: {args.name}", file=sys.stderr)
        return 2
    profile = profiles[args.name]
    if args.profile_cmd == "show":
        emit({"profile": profile}, args.json)
        return 0
    planned = profile_changes(profile)
    result = {"dry_run": args.dry_run, "profile": profile, "planned_changes": planned}
    if not args.dry_run:
        manifest = create_backup(
            [
                active_profile_path(),
                settings_path(),
                active_hyprland_conf(),
                active_hyprland_input_lua(),
            ],
            f"profile apply {args.name}",
        )
        write_json(active_profile_path(), profile)
        set_nested_setting("profile.active", args.name)
        set_nested_setting("terminal.default_mode", profile.get("terminal_default_mode", "light"))
        set_nested_setting("motion.active", profile.get("motion_preset", "balanced"))
        apply_profile_files(profile)
        result["backup_id"] = manifest["backup_id"]
    emit(result, args.json)
    return 0


def handle_motion(args: argparse.Namespace) -> int:
    if args.motion_cmd == "list":
        emit({"presets": MOTION_PRESETS}, args.json)
        return 0
    if args.name not in MOTION_PRESETS:
        print(f"Unknown motion preset: {args.name}", file=sys.stderr)
        return 2
    preset = MOTION_PRESETS[args.name]
    if args.motion_cmd == "show":
        emit({"preset": preset}, args.json)
        return 0
    result = {
        "dry_run": args.dry_run,
        "preset": preset,
        "planned_changes": {
            "kitty:cursor_trail": str(preset["kitty_cursor_trail"]),
            "ghostty:cursor_shader": str(preset["ghostty_cursor_shader"]),
            "hyprland:animation": str(preset["hyprland_animation"]),
        },
    }
    if not args.dry_run:
        manifest = create_backup(
            [active_motion_path(), settings_path(), active_kitty_ui(), active_ghostty_config()],
            f"motion apply {args.name}",
        )
        write_json(active_motion_path(), preset)
        set_nested_setting("motion.active", args.name)
        apply_motion_files(preset)
        result["backup_id"] = manifest["backup_id"]
    emit(result, args.json)
    return 0


def handle_settings(args: argparse.Namespace) -> int:
    if args.settings_cmd == "schema":
        emit(settings_schema(), args.json)
        return 0
    if args.settings_cmd == "validate":
        report = validate_settings()
        emit(report, args.json)
        return 0 if report["valid"] else 1
    if args.settings_cmd == "get":
        emit({"key": args.key, "value": settings_get(args.key)}, args.json)
        return 0
    if args.settings_cmd == "list":
        emit({"settings": settings_get()}, args.json)
        return 0
    try:
        emit(settings_set(args.key, args.value), args.json)
        return 0
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def handle_installer(args: argparse.Namespace) -> int:
    if args.installer_cmd == "plan":
        emit(installer_plan(), args.json)
        return 0
    return 2


def handle_backup(args: argparse.Namespace) -> int:
    try:
        if args.backup_cmd == "create":
            emit(create_backup([Path(path) for path in args.paths], args.reason), args.json)
            return 0
        if args.backup_cmd == "list":
            emit({"backups": list_backups()}, args.json)
            return 0
        if args.backup_cmd == "restore":
            emit(restore_backup(args.backup_id, args.dry_run), args.json)
            return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


# ---------------------------------------------------------------------------
# Theme activation transaction (design §7/§8, R4/R7; tasks 5.3/5.5)
# ---------------------------------------------------------------------------

# User choice -> (base mode, render profile) per design §7 table.
THEME_CHOICES: dict[str, tuple[str, str]] = {
    "light": ("light", "standard"),
    "dark": ("dark", "standard"),
    "night": ("dark", "night"),
}


class ThemeActivationError(RuntimeError):
    """Blocking post-commit failure (selector/reload) forcing a full rollback."""


def _capture_path(path: Path) -> dict[str, Any]:
    """Capture one mutable path's exact state: symlink target or file bytes."""
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if path.exists():
        return {"kind": "file", "data": path.read_bytes()}
    return {"kind": "absent"}


def _restore_path(path: Path, state: dict[str, Any]) -> None:
    if path.is_symlink() or path.exists():
        path.unlink()
    kind = state["kind"]
    if kind == "symlink":
        path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(state["target"], path)
    elif kind == "file":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(state["data"])


def _capture_directory(directory: Path) -> dict[str, Any]:
    """Capture a directory's file/link inventory (rollback of cleanup and of
    files created through flipped bridge symlinks)."""
    if not directory.is_dir():
        return {}
    captured: dict[str, Any] = {}
    for child in directory.iterdir():
        if child.is_symlink():
            captured[child.name] = ("link", os.readlink(child))
        elif child.is_file():
            captured[child.name] = ("file", child.read_bytes())
    return captured


def _restore_directory(
    directory: Path, captured: dict[str, Any], *, json_only: bool = False
) -> None:
    if not directory.is_dir():
        return
    for child in directory.iterdir():
        if json_only and child.suffix != ".json":
            continue
        if (child.is_symlink() or child.is_file()) and child.name not in captured:
            child.unlink()
    for name, (kind, value) in captured.items():
        target = directory / name
        if not name or Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError(f"unsafe restore entry name: {name!r}")
        if kind == "link":
            if target.is_symlink():
                if os.readlink(target) == value:
                    continue
                target.unlink()
            elif target.exists():
                target.unlink()
            os.symlink(value, target)
        else:
            target.write_bytes(value)


def _herdr_active_config_path(config_home: Path) -> Path:
    """Resolve the Herdr active-config path for rollback snapshotting only.

    Mirrors ``herdr_switch.resolve_selector``'s precedence; the active config
    is the documented selector, so an existing symlink here is a valid
    rollback target rather than a rejected activation source.
    """
    override = os.environ.get("HERDR_CONFIG_PATH")
    if override:
        return Path(override)
    return config_home / "herdr" / "config.toml"


def _mutable_paths(paths: Any) -> list[Path]:
    """Every mutable active path + selector file the activation can touch.

    Union of the paths written by ``sync_active_targets``, the active bat theme
    variants, the adapter-touched symlink/selector surface (design §7 reload
    section), the settings file, and — when repo generation is enabled — the
    stable repo files that carry the active palette (rollback of "partial
    cross-target state", R4).
    """
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    mutable = [
        paths.kitty,
        paths.kitty_config,
        paths.kitty_ui,
        paths.ghostty,
        paths.ghostty_config,
        paths.warp,
        paths.warp_settings,
        paths.opencode,
        paths.opencode_tui,
        paths.codex_theme,
        paths.codex_config,
        paths.pi_theme,
        paths.pi_settings,
        paths.starship,
        paths.tmux,
        paths.lazygit,
        paths.zellij_config,
        paths.nvim,
        paths.zsh_syntax,
        paths.ls_colors,
        paths.bat,
        paths.delta,
        paths.fzf,
        paths.btop,
        paths.dunst,
        paths.firefox,
        paths.obsidian,
        paths.cava,
        paths.hyprland,
        paths.hypr_colors_lua,
        paths.hypr_colors_conf,
        paths.waybar,
        paths.waybar_matugen,
        paths.rofi,
        paths.rofi_matugen,
        paths.bat_theme_dir / "Dreamcoder.tmTheme",
        paths.bat_theme_dir / "Dreamcoder-Dark.tmTheme",
        paths.bat_theme_dir / "Dreamcoder-Light.tmTheme",
        settings_path(),
        # Adapter-touched system/symlink surface (design §7 reload section).
        config_home / "btop/themes/dreamcoder.theme",
        config_home / "dunst/dreamcoder-dunst.conf",
        config_home / "git/delta-dreamcoder.gitconfig",
        config_home / "lazygit/config.yml",
        config_home / "hypr/dreamcoder-colors.lua",
        _herdr_active_config_path(config_home),
        cache_home / "dreamcoder/cursor-cli.env",
    ]
    if write_repo_enabled():
        mutable += [
            ROOT / "DreamcoderKitty/.config/kitty/dreamcoder-ui.conf",
            ROOT / ".opencode/themes/dreamcoder.json",
            ROOT / "DreamcoderCodexApp/Dreamcoder.codex-theme.json",
            ROOT / "DreamcoderCodexCLI/Dreamcoder.tmTheme",
            ROOT / "DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme",
            ROOT / "DreamcoderPi/.pi/agent/themes/dreamcoder.json",
            ROOT / "DreamcoderAntigravity/Dreamcoder.json",
            ROOT / "DreamcoderThemes/dreamcoder/hyprland.conf",
            ROOT / "DreamcoderThemes/dreamcoder/waybar.css",
            ROOT / "DreamcoderThemes/dreamcoder/rofi.rasi",
        ]
    return mutable


def _bridge_variant(base: str, profile: str) -> str:
    return "night" if profile == "night" else base


def _flip_bridge_symlinks(paths: Any, base: str, profile: str) -> None:
    """Select the correct variant target for matugen bridge symlinks (design §6).

    Only flips paths that are already symlinks — regular files are written
    directly by the sync writers. The activation transaction snapshots these
    before the flip, so a rollback restores the prior link targets exactly.
    """
    variant = _bridge_variant(base, profile)
    bridges = [
        (paths.waybar_matugen, f"colors-{variant}.css"),
        (paths.rofi_matugen, f"colors-{variant}.rasi"),
        (paths.hypr_colors_lua, f"colors-{variant}.lua"),
        (paths.hypr_colors_conf, f"colors-{variant}.conf"),
        (paths.kitty, f"colors-dreamcoder-{variant}.conf"),
        (paths.kitty_ui, f"dreamcoder-ui-{variant}.conf"),
    ]
    for link, target in bridges:
        if link.is_symlink():
            link.unlink()
            os.symlink(target, link)


def run_reload_adapter(base: str, profile: str) -> None:
    """Invoke the bounded post-validation system/reload adapter (design §7).

    ``scripts/apply-theme-mode.sh`` owns the system-mode, symlink, and reload
    surface and runs only after preparation and settings persistence succeeded.
    The adapter skips its own preparation when ``DREAMCODER_SYNC_DONE=1`` (this
    call), so it can never re-validate or re-commit. A non-zero exit is a
    blocking reload failure: the caller rolls the whole transaction back.
    """
    script = ROOT / "scripts" / "apply-theme-mode.sh"
    if not script.is_file():
        return
    env = os.environ.copy()
    env.update(
        {
            "DREAMCODER_THEME_MODE": base,
            "DREAMCODER_THEME_PROFILE": profile,
            "DREAMCODER_SYNC_DONE": "1",
        }
    )
    proc = subprocess.run(
        [str(script), base, env.get("DREAMCODER_WALLPAPER", ""), profile],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise ThemeActivationError(
            f"reload adapter exited {proc.returncode}: {proc.stderr.strip() or proc.stdout.strip()}"
        )


def _regenerate_prior(paths: Any, prior_base: str, prior_profile: str) -> None:
    """Best-effort regeneration of the prior profile after a rollback.

    Snapshots already restore every mutable path byte-for-byte; regeneration is
    a safety net for deterministic repo artifacts and never masks the original
    failure (``write_if_changed`` skips identical content).
    """
    # Best-effort by contract: any regeneration failure must not mask the
    # original activation error this rollback is recovering from.
    with contextlib.suppress(Exception):
        prepared = sync.prepare(prior_base, prior_profile)
        sync.sync_active_targets(paths, prepared.active, prior_base, prior_profile)
        sync.sync_bat_theme_variants(paths, prepared.variants)
        if write_repo_enabled():
            sync.sync_repo_snippets(prepared.variants, prepared.active)


def _commit_activation(
    paths: Any,
    prepared: sync.PreparedSync,
    base: str,
    profile: str,
    changed: dict[str, bool],
) -> None:
    """Commit one prepared activation: persist, flip bridges, write, validate.

    Runs inside the activation transaction's try block; any exception here
    (write failure, invalid post-write selector, blocking reload failure)
    triggers a full snapshot rollback in the caller.
    """
    # 4. Persist settings before applying the base mode (R7: light/dark
    #    explicitly persist standard and exit Night).
    set_nested_setting("terminal.default_mode", base)
    set_nested_setting("theme.render_profile", profile)
    # 5. Flip matugen bridge symlinks to the target variant before the writers
    #    run (design §6: "select colors-night.css before commit").
    _flip_bridge_symlinks(paths, base, profile)
    # 6. Commit variants, active files, and selectors. write_if_changed()
    #    semantics are preserved — each entry reports bool changed.
    changed.update(sync.sync_active_targets(paths, prepared.active, base, profile))
    bat_changes = sync.sync_bat_theme_variants(paths, prepared.variants)
    if write_repo_enabled():
        repo_changes = sync.sync_repo_snippets(prepared.variants, prepared.active)
        changed["repo_changes"] = any(repo_changes)
    changed["bat_theme_variants"] = any(bat_changes)
    # 7. Post-write validation: an invalid selector is blocking.
    if not valid_starship(paths.starship):
        raise ThemeActivationError(f"Generated Starship config is invalid: {paths.starship}")
    # 8. Bounded system/reload adapter; a blocking reload failure rolls back.
    if os.environ.get("DREAMCODER_SYNC_DONE") != "1":
        run_reload_adapter(base, profile)


def apply_theme(base: str, profile: str, choice: str, as_json: bool) -> int:
    """Activate a (base, profile) pair as one transaction (design §7/§8).

    Order: prepare+validate (zero writes) -> snapshot every mutable active path
    + selector file + settings -> persist settings -> flip bridge symlinks ->
    commit variants/active files/selectors -> post-write validation -> bounded
    system/reload adapter. Any exception, invalid post-write selector, blocking
    reload failure, or incomplete coverage restores snapshots and prior settings
    and regenerates the prior profile before returning non-zero.
    """
    paths = theme_paths()
    # 1. Prepare + validate: a failed gate exits before any persistence, write,
    #    symlink change, cleanup, system-mode change, or reload (R4/R8).
    try:
        prepared = sync.prepare(base, profile)
    except sync.ThemeGateError as exc:
        if as_json:
            emit(
                {
                    "requested": choice,
                    "effective_base": base,
                    "effective_profile": profile,
                    "coverage": "0/0",
                    "changed": {},
                    "rollback_state": "rejected",
                    "errors": list(exc.errors),
                },
                True,
            )
        else:
            print(str(exc), file=sys.stderr)
        return 1

    # 2. Prior persisted state (the rollback target).
    prior_base = settings_get("terminal.default_mode")
    prior_profile = settings_get("theme.render_profile")
    prior_base = prior_base if prior_base in {"light", "dark"} else "light"
    prior_profile = prior_profile if prior_profile in {"standard", "night"} else "standard"

    # 3. Snapshot every mutable active path + selector file BEFORE the first
    #    mutation (design §4: "snapshot settings and every mutable active path").
    snapshots: dict[str, dict[str, Any]] = {}
    for path in _mutable_paths(paths):
        snapshots[str(path)] = _capture_path(path)
    dir_captures: dict[str, dict[str, Any]] = {}
    if os.environ.get("DREAMCODER_CLEAN_OPENCODE_THEMES", "1") != "0":
        dir_captures[str(paths.opencode.parent)] = _capture_directory(paths.opencode.parent)
    for bridge in (
        paths.waybar_matugen,
        paths.rofi_matugen,
        paths.hypr_colors_lua,
        paths.hypr_colors_conf,
        paths.kitty,
        paths.kitty_ui,
    ):
        if bridge.parent.is_dir():
            dir_captures.setdefault(str(bridge.parent), _capture_directory(bridge.parent))

    rollback_state = "none"
    changed: dict[str, bool] = {}
    try:
        _commit_activation(paths, prepared, base, profile, changed)
    except Exception as exc:
        rollback_state = "restored"
        _restore_snapshots(snapshots, dir_captures)
        set_nested_setting("terminal.default_mode", prior_base)
        set_nested_setting("theme.render_profile", prior_profile)
        _regenerate_prior(paths, prior_base, prior_profile)
        if as_json:
            emit(
                {
                    "requested": choice,
                    "effective_base": prior_base,
                    "effective_profile": prior_profile,
                    "coverage": f"{len(prepared.coverage)}/{len(prepared.coverage)}",
                    "changed": {},
                    "rollback_state": rollback_state,
                    "error": str(exc),
                },
                True,
            )
        else:
            print(f"theme activation failed: {exc}", file=sys.stderr)
            print("rollback_state: restored", file=sys.stderr)
        return 1

    status = {
        "requested": choice,
        "effective_base": base,
        "effective_profile": profile,
        "coverage": f"{len(prepared.coverage)}/{len(prepared.coverage)}",
        "changed": changed,
        "rollback_state": rollback_state,
    }
    emit(status, as_json)
    return 0


def _restore_snapshots(
    snapshots: dict[str, dict[str, Any]], dir_captures: dict[str, dict[str, Any]]
) -> None:
    for path_str, state in snapshots.items():
        _restore_path(Path(path_str), state)
    for dir_str, captured in dir_captures.items():
        _restore_directory(Path(dir_str), captured, json_only=Path(dir_str).name == "opencode")


def handle_theme(args: argparse.Namespace) -> int:
    """Activate a theme base mode + render profile (design §7)."""
    if args.theme_cmd != "apply":
        return 2
    base, profile = THEME_CHOICES[args.choice]
    return apply_theme(base, profile, args.choice, args.json)
