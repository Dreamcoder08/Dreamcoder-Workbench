"""Argument parser for Dreamcoder Control Center."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dreamcoder-control", description="Dreamcoder Control Center"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    doctor = sub.add_parser("doctor", help="Run structured health checks")
    doctor.add_argument("--json", action="store_true")

    dashboard = sub.add_parser("dashboard", help="Show the Dreamcoder Control Center dashboard")
    dashboard_format = dashboard.add_mutually_exclusive_group()
    dashboard_format.add_argument("--json", action="store_true")
    dashboard_format.add_argument("--markdown", action="store_true")

    tui = sub.add_parser("tui", help="Render or apply the terminal settings UI")
    tui_sub = tui.add_subparsers(dest="tui_cmd", required=True)
    tui_render = tui_sub.add_parser("render")
    tui_render.add_argument("--json", action="store_true")
    tui_set = tui_sub.add_parser("set")
    tui_set.add_argument("key")
    tui_set.add_argument("value")
    tui_set.add_argument("--dry-run", action="store_true")
    tui_set.add_argument("--json", action="store_true")

    docs = sub.add_parser("docs", help="Generate visual Dreamcoder documentation")
    docs_sub = docs.add_subparsers(dest="docs_cmd", required=True)
    docs_report = docs_sub.add_parser("report")
    docs_report.add_argument("--json", action="store_true")
    docs_report.add_argument("--markdown", action="store_true")
    docs_report.add_argument("--write", action="store_true")

    audit = sub.add_parser(
        "audit", help="Compare Dreamcoder capabilities against dotfile baselines"
    )
    audit_sub = audit.add_subparsers(dest="audit_cmd", required=True)
    audit_compare = audit_sub.add_parser("compare")
    audit_compare.add_argument("--json", action="store_true")
    audit_compare.add_argument("--markdown", action="store_true")

    settings = sub.add_parser("settings", help="Read or write Dreamcoder settings")
    settings_sub = settings.add_subparsers(dest="settings_cmd", required=True)
    settings_sub.add_parser("list").add_argument("--json", action="store_true")
    settings_sub.add_parser("schema").add_argument("--json", action="store_true")
    settings_sub.add_parser("validate").add_argument("--json", action="store_true")
    settings_get_p = settings_sub.add_parser("get")
    settings_get_p.add_argument("key")
    settings_get_p.add_argument("--json", action="store_true")
    settings_set_p = settings_sub.add_parser("set")
    settings_set_p.add_argument("key")
    settings_set_p.add_argument("value")
    settings_set_p.add_argument("--json", action="store_true")

    profile = sub.add_parser("profile", help="Manage machine profiles")
    profile_sub = profile.add_subparsers(dest="profile_cmd", required=True)
    profile_sub.add_parser("list").add_argument("--json", action="store_true")
    profile_show = profile_sub.add_parser("show")
    profile_show.add_argument("name")
    profile_show.add_argument("--json", action="store_true")
    profile_apply = profile_sub.add_parser("apply")
    profile_apply.add_argument("name")
    profile_apply.add_argument("--dry-run", action="store_true")
    profile_apply.add_argument("--json", action="store_true")

    motion = sub.add_parser("motion", help="Manage motion presets")
    motion_sub = motion.add_subparsers(dest="motion_cmd", required=True)
    motion_sub.add_parser("list").add_argument("--json", action="store_true")
    motion_show = motion_sub.add_parser("show")
    motion_show.add_argument("name")
    motion_show.add_argument("--json", action="store_true")
    motion_apply = motion_sub.add_parser("apply")
    motion_apply.add_argument("name")
    motion_apply.add_argument("--dry-run", action="store_true")
    motion_apply.add_argument("--json", action="store_true")

    installer = sub.add_parser("installer", help="Inspect installer targets and conflicts")
    installer_sub = installer.add_subparsers(dest="installer_cmd", required=True)
    installer_sub.add_parser("plan").add_argument("--json", action="store_true")

    repair = sub.add_parser("repair", help="Plan and apply safe Dreamcoder repairs")
    repair_sub = repair.add_subparsers(dest="repair_cmd", required=True)
    repair_sub.add_parser("catalog").add_argument("--json", action="store_true")
    repair_sub.add_parser("plan").add_argument("--json", action="store_true")
    repair_apply = repair_sub.add_parser("apply")
    repair_apply.add_argument("--dry-run", action="store_true")
    repair_apply.add_argument("--json", action="store_true")

    visual = sub.add_parser("visual", help="Plan screenshot-based visual regression")
    visual_sub = visual.add_subparsers(dest="visual_cmd", required=True)
    visual_plan_p = visual_sub.add_parser("plan")
    visual_plan_p.add_argument("--json", action="store_true")
    visual_plan_p.add_argument("--markdown", action="store_true")
    visual_audit_p = visual_sub.add_parser("audit")
    visual_audit_p.add_argument("--json", action="store_true")
    visual_audit_p.add_argument("--markdown", action="store_true")

    backup = sub.add_parser("backup", help="Create and restore Dreamcoder backup manifests")
    backup_sub = backup.add_subparsers(dest="backup_cmd", required=True)
    backup_create = backup_sub.add_parser("create")
    backup_create.add_argument("paths", nargs="+")
    backup_create.add_argument("--reason", default="manual backup")
    backup_create.add_argument("--json", action="store_true")
    backup_sub.add_parser("list").add_argument("--json", action="store_true")
    backup_restore = backup_sub.add_parser("restore")
    backup_restore.add_argument("backup_id")
    backup_restore.add_argument("--dry-run", action="store_true")
    backup_restore.add_argument("--json", action="store_true")

    theme = sub.add_parser("theme", help="Activate the Dreamcoder Light or Dark theme")
    theme_sub = theme.add_subparsers(dest="theme_cmd", required=True)
    theme_apply = theme_sub.add_parser("apply", help="Apply a theme choice as one transaction")
    theme_apply.add_argument("choice", choices=["light", "dark"], help="Theme choice to activate")
    theme_apply.add_argument("--json", action="store_true")
    return parser
