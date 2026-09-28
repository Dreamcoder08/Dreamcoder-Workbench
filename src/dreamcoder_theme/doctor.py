"""Structured health checks for Dreamcoder Dots."""

from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from .core import (
    VALID_STATUSES,
    command_exists,
    config_home,
    data_home,
    detect_mode_from_file,
    shell_stdout,
)
from .installer import installer_plan


@dataclass(frozen=True)
class HealthCheck:
    name: str
    status: str
    detail: str
    repair: str

    def to_dict(self) -> dict[str, str]:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid health status: {self.status}")
        return asdict(self)


def summarize_checks(checks: list[dict[str, str]]) -> dict[str, int]:
    return {
        "ok": sum(1 for check in checks if check["status"] == "ok"),
        "warn": sum(1 for check in checks if check["status"] == "warn"),
        "fail": sum(1 for check in checks if check["status"] == "fail"),
        "skip": sum(1 for check in checks if check["status"] == "skip"),
    }


def _check_hypr_colors_loader(ch: Path) -> HealthCheck:
    """Check that Hyprland loads dreamcoder-colors.

    The loader belongs in custom.lua: Dreamcoder generates it and ML4W never
    ships it, so ML4W upgrades that rewrite hyprland.lua cannot drop it. A
    require injected into hyprland.lua is still accepted as a legacy layout.
    """
    hypr = ch / "hypr"
    for candidate in (hypr / "custom.lua", hypr / "hyprland.lua"):
        if candidate.exists() and "dreamcoder-colors" in candidate.read_text(errors="ignore"):
            return HealthCheck(
                name="hyprland dreamcoder import",
                status="ok",
                detail=str(candidate),
                repair="",
            )
    return HealthCheck(
        name="hyprland dreamcoder import",
        status="warn",
        detail=f"no dreamcoder-colors loader in {hypr / 'custom.lua'}",
        repair="scripts/generate-custom-lua.sh (custom.lua loads dreamcoder-colors)",
    )


def _check_ml4w_hooks(ch: Path) -> list[HealthCheck]:
    """Check ML4W integration hooks."""
    ml4w_checks: list[HealthCheck] = []

    ml4w_checks.append(_check_hypr_colors_loader(ch))

    # Btop theme
    btop_theme = ch / "btop" / "themes" / "dreamcoder.theme"
    btop_ok = btop_theme.exists()
    if btop_ok:
        btop_conf = ch / "btop" / "btop.conf"
        if btop_conf.exists():
            btop_theme_ref = "dreamcoder" in btop_conf.read_text(errors="ignore")
            if not btop_theme_ref:
                btop_ok = False
    ml4w_checks.append(
        HealthCheck(
            name="btop dreamcoder theme",
            status="ok" if btop_ok else "warn",
            detail=str(btop_theme) if btop_theme.exists() else "missing",
            repair=(
                "cp DreamcoderThemes/dreamcoder/btop-dreamcoder.theme"
                " ~/.config/btop/themes/dreamcoder.theme"
            ),
        )
    )

    # Bat theme
    bat_themes = data_home() / "bat" / "themes"
    bat_ok = (bat_themes / "Dreamcoder-Dark.tmTheme").exists()
    if not bat_ok:
        bat_themes_alt = ch / "bat" / "themes"
        bat_ok = (bat_themes_alt / "Dreamcoder-Dark.tmTheme").exists()
    ml4w_checks.append(
        HealthCheck(
            name="bat dreamcoder theme",
            status="ok" if bat_ok else "warn",
            detail="Dreamcoder-Dark.tmTheme" if bat_ok else "missing",
            repair="dreamcoder-theme sync (generates bat themes)",
        )
    )

    # GTK color scheme matches mode
    if command_exists("gsettings"):
        gtk_result = shell_stdout(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"]
        )
        gtk_prefer_dark = "dark" in (gtk_result.stdout or "").lower()
        current_mode = detect_mode_from_file(ch / "kitty" / "colors-dreamcoder.conf")
        mode_mismatch = (current_mode == "dark" and not gtk_prefer_dark) or (
            current_mode == "light" and gtk_prefer_dark
        )
        ml4w_checks.append(
            HealthCheck(
                name="gtk color scheme",
                status="warn" if mode_mismatch else "ok",
                detail=(gtk_result.stdout or "unknown").strip(),
                repair="gsettings set org.gnome.desktop.interface color-scheme prefer-dark",
            )
        )
    else:
        ml4w_checks.append(
            HealthCheck(
                name="gtk color scheme",
                status="skip",
                detail="gsettings unavailable",
                repair="",
            )
        )

    # Waybar/Rofi symlinks
    for comp, symlink, variant in [
        ("waybar", ch / "waybar" / "colors.css", "colors-{mode}.css"),
        ("rofi", ch / "rofi" / "colors.rasi", "colors-{mode}.rasi"),
    ]:
        sl_status = "ok"
        sl_detail = f"{symlink}"
        if symlink.is_symlink():
            target = symlink.readlink()
            sl_detail = f"{symlink} -> {target}"
        elif symlink.exists():
            sl_status = "warn"
            sl_detail = f"{symlink} exists but is NOT a symlink"
        else:
            sl_status = "fail"
            sl_detail = f"{symlink} missing"
        ml4w_checks.append(
            HealthCheck(
                name=f"{comp} colors symlink",
                status=sl_status,
                detail=sl_detail,
                repair=f"ln -sf {variant} {symlink}",
            )
        )

    return ml4w_checks


def _check_optional_themes() -> list[HealthCheck]:
    """Check optional app theme files."""
    opt_checks: list[HealthCheck] = []

    firefox_dirs = list(Path.home().glob(".mozilla/firefox/*.default*/chrome/dreamcoder*.css"))
    opt_checks.append(
        HealthCheck(
            name="firefox dreamcoder theme",
            status="ok" if firefox_dirs else "warn",
            detail=f"{len(firefox_dirs)} file(s)" if firefox_dirs else "not found",
            repair="Copy DreamcoderThemes/firefox-dreamcoder.css to ~/.mozilla/firefox/*.default/chrome/",
        )
    )

    obsidian_css = Path.home() / ".config/obsidian/dreamcoder.css"
    opt_checks.append(
        HealthCheck(
            name="obsidian dreamcoder theme",
            status="ok" if obsidian_css.exists() else "warn",
            detail="found" if obsidian_css.exists() else "not found",
            repair="Copy DreamcoderThemes/obsidian-dreamcoder.css to ~/.config/obsidian/dreamcoder.css",
        )
    )

    cava_config = config_home() / "cava" / "dreamcoder.config"
    opt_checks.append(
        HealthCheck(
            name="cava dreamcoder config",
            status="ok" if cava_config.exists() else "warn",
            detail="found" if cava_config.exists() else "not found",
            repair="Copy DreamcoderThemes/cava-dreamcoder.config to ~/.config/cava/dreamcoder.config",
        )
    )

    return opt_checks


def _check_backup_freshness() -> list[HealthCheck]:
    """Check backup manifest freshness."""
    backups_dir = data_home() / "dreamcoder" / "backups"
    fresh = False
    manifests: list[Path] = []
    if backups_dir.exists():
        manifests = sorted(backups_dir.glob("*/manifest.json"))
        if manifests:
            fresh = True
    return [
        HealthCheck(
            name="backup manifest",
            status="ok" if fresh else "warn",
            detail=f"{len(manifests)} backup(s)" if fresh else "no backups",
            repair="./scripts/dreamcoder backup create --reason doctor",
        )
    ]


def doctor_checks() -> list[HealthCheck]:
    ch = config_home()
    checks: list[HealthCheck] = []
    critical_paths = {
        "kitty config": ch / "kitty",
        "ghostty config": ch / "ghostty",
        "starship config": ch / "starship.toml",
        "fish config": ch / "fish" / "config.fish",
    }
    for name, path in critical_paths.items():
        checks.append(
            HealthCheck(
                name=name,
                status="ok" if path.exists() else "fail",
                detail=str(path),
                repair="./scripts/dreamcoder repair",
            )
        )

    kitty_ui = ch / "kitty" / "dreamcoder-ui.conf"
    duplicate_include = kitty_ui.exists() and any(
        line.strip() == "include colors-dreamcoder.conf"
        for line in kitty_ui.read_text(errors="ignore").splitlines()
    )
    checks.append(
        HealthCheck(
            name="kitty duplicate color include",
            status="fail" if duplicate_include else "ok",
            detail="dreamcoder-ui.conf must not include colors-dreamcoder.conf after kitty.conf already does",
            repair="./scripts/dreamcoder sync",
        )
    )

    mode = detect_mode_from_file(ch / "kitty" / "colors-dreamcoder.conf")
    checks.append(
        HealthCheck(
            name="active theme mode",
            status="ok" if mode in {"light", "dark"} else "warn",
            detail=mode,
            repair="./scripts/dreamcoder auto",
        )
    )

    checks.append(
        HealthCheck(
            name="starship binary",
            status="ok" if command_exists("starship") else "fail",
            detail=shutil.which("starship") or "missing",
            repair="Install starship, then run ./scripts/dreamcoder repair",
        )
    )
    checks.append(
        HealthCheck(
            name="fish binary",
            status="ok" if command_exists("fish") else "fail",
            detail=shutil.which("fish") or "missing",
            repair="Install fish, then run ./scripts/dreamcoder repair",
        )
    )

    timer_status = "skip"
    timer_detail = "systemctl unavailable"
    if command_exists("systemctl"):
        result = shell_stdout(["systemctl", "--user", "is-active", "dreamcoder-theme-auto.timer"])
        timer_detail = (result.stdout or result.stderr).strip() or "unknown"
        timer_status = "ok" if result.returncode == 0 and timer_detail == "active" else "warn"
    checks.append(
        HealthCheck(
            name="light/dark timer",
            status=timer_status,
            detail=timer_detail,
            repair="systemctl --user enable --now dreamcoder-theme-auto.timer",
        )
    )

    conflicts = installer_plan()["conflicts"]
    checks.append(
        HealthCheck(
            name="installer conflicts",
            status="ok" if not conflicts else "warn",
            detail=f"{len(conflicts)} conflict(s)",
            repair="./scripts/dreamcoder installer plan --json",
        )
    )

    # --- New checks: delegate to helpers ---
    checks.extend(_check_ml4w_hooks(ch))
    checks.extend(_check_optional_themes())
    checks.extend(_check_backup_freshness())

    return checks


def doctor_report() -> dict[str, object]:
    checks = [check.to_dict() for check in doctor_checks()]
    return {"schema": "dreamcoder.doctor.v1", "summary": summarize_checks(checks), "checks": checks}
