"""Orchestrate Dreamcoder theme generation."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

from .herdr_contract import SUPPORTED_PROFILES, HerdrProfile
from .palette import (
    adaptive_palette,
    load_guardrails,
    load_render_profile,
    load_variants,
    night_palette,
    validate_palette,
)
from .palette_tokens import VARIANTS as DEFAULT_VARIANTS
from .renderers import (
    antigravity_content,
    bat_content,
    btop_content,
    cava_content,
    codex_tmtheme_content,
    delta_content,
    dunst_content,
    firefox_content,
    fzf_content,
    ghostty_content,
    herdr_content,
    hypr_colors_conf_content,
    hypr_colors_lua_content,
    hypr_content,
    kitty_content,
    kitty_ui_content,
    lazygit_content,
    ls_colors_content,
    nvim_content,
    nvim_dispatcher_content,
    obsidian_content,
    opencode_content,
    pi_theme_content,
    readme_content,
    rofi_content,
    rofi_matugen_content,
    starship_content,
    tmux_content,
    warp_content,
    waybar_content,
    waybar_matugen_content,
    zellij_content,
    zsh_syntax_content,
)
from .renderers_orca import sync_orca_theme
from .settings import (
    ROOT,
    VALID_RENDER_PROFILES,
    adaptive_enabled,
    render_profile,
    theme_mode,
    theme_paths,
    write_repo_enabled,
)
from .writers import (
    cleanup_opencode_themes,
    ensure_codex_theme_config,
    ensure_kitty_ui_include,
    ensure_pi_theme_settings,
    update_ghostty_theme,
    update_warp_settings,
    update_zellij_config,
    valid_starship,
    write_if_changed,
    write_opencode_tui,
    write_variant_files,
)


class ThemeGateError(RuntimeError):
    """Raised by ``prepare()`` when the dual gate or coverage assertion fails.

    Carries the structured failure list (metric/profile/pair/measured/
    threshold for WCAG+APCA, or the coverage problems) and renders the
    fail-closed message main() and the CLI handler surface. It is raised
    before any writer, selector, or settings mutation (R4/R8, design §4/§8).
    """

    def __init__(self, errors: Sequence[str], *, kind: str = "Theme gate failed") -> None:
        self.errors = tuple(errors)
        super().__init__(
            f"{kind} — no writes performed:\n" + "\n".join(f"  - {error}" for error in errors)
        )


@dataclass(frozen=True)
class PreparedSync:
    """Immutable result of validation-first preparation (design §4, ADR-004).

    ``prepare()`` produces this with ZERO filesystem writes: the validated
    active palette, the dark/light/night render-variant map, the frozen
    33-consumer coverage declaration, and the in-memory render of every
    coverage consumer. The caller (``main()`` or the CLI activation
    transaction) owns the commit.
    """

    mode: str
    profile: str
    active: dict[str, str]
    variants: dict[str, dict[str, str]]
    coverage: tuple[CoverageRow, ...]
    render_plan: Mapping[str, str]


def sync_active_targets(
    paths: Any, active: dict[str, str], mode: str, profile: str = "standard"
) -> dict[str, bool]:
    return {
        "kitty": write_if_changed(paths.kitty, kitty_content(active)),
        "kitty_ui": write_if_changed(paths.kitty_ui, kitty_ui_content(active)),
        "kitty_config": ensure_kitty_ui_include(paths.kitty_config),
        "ghostty": write_if_changed(paths.ghostty, ghostty_content(active)),
        "ghostty_config": update_ghostty_theme(paths.ghostty_config, mode, profile),
        "warp": write_if_changed(paths.warp, warp_content(active)),
        "warp_settings": update_warp_settings(paths.warp_settings, mode, profile),
        "opencode": write_if_changed(
            paths.opencode, opencode_content(active, transparent_background=True)
        ),
        "opencode_tui": write_opencode_tui(paths.opencode_tui),
        "opencode_cleanup": cleanup_opencode_themes(paths.opencode),
        "codex_theme": write_if_changed(paths.codex_theme, codex_tmtheme_content(active)),
        "bat_theme": write_if_changed(
            paths.bat_theme_dir / "Dreamcoder.tmTheme", codex_tmtheme_content(active)
        ),
        "codex_config": ensure_codex_theme_config(paths.codex_config),
        "pi_theme": write_if_changed(paths.pi_theme, pi_theme_content(active)),
        "pi_settings": ensure_pi_theme_settings(paths.pi_settings),
        "starship": write_if_changed(paths.starship, starship_content(active)),
        "tmux": write_if_changed(paths.tmux, tmux_content(active)),
        "lazygit": write_if_changed(paths.lazygit, lazygit_content(active)),
        "zellij": update_zellij_config(paths.zellij_config, mode, profile),
        # New targets
        "nvim": write_if_changed(paths.nvim, nvim_dispatcher_content()),
        "zsh_syntax": write_if_changed(paths.zsh_syntax, zsh_syntax_content(active)),
        "ls_colors": write_if_changed(paths.ls_colors, ls_colors_content(active)),
        "bat": write_if_changed(paths.bat, bat_content(active)),
        "delta": write_if_changed(paths.delta, delta_content(active)),
        "fzf": write_if_changed(paths.fzf, fzf_content(active)),
        "btop": write_if_changed(paths.btop, btop_content(active)),
        "dunst": write_if_changed(paths.dunst, dunst_content(active)),
        "firefox": write_if_changed(paths.firefox, firefox_content(active)),
        "obsidian": write_if_changed(paths.obsidian, obsidian_content(active)),
        "cava": write_if_changed(paths.cava, cava_content(active)),
        # Desktop/WM targets
        "hyprland": write_if_changed(paths.hyprland, hypr_content(active)),
        "hypr_colors_lua": write_if_changed(paths.hypr_colors_lua, hypr_colors_lua_content(active)),
        "hypr_colors_conf": write_if_changed(
            paths.hypr_colors_conf, hypr_colors_conf_content(active)
        ),
        "waybar": write_if_changed(paths.waybar, waybar_content(active)),
        "waybar_matugen": write_if_changed(paths.waybar_matugen, waybar_matugen_content(active)),
        "rofi": write_if_changed(paths.rofi, rofi_content(active)),
        "rofi_matugen": write_if_changed(paths.rofi_matugen, rofi_matugen_content(active)),
    }


# ------------------------------------------------------------------
# Declarative variant registry — each entry produces write_variant_files
# (+ active-file write when active_path is set). Uniform entries only;
# hyprland, waybar, rofi, nvim, and opencode-transparent
# stay as explicit calls below the loop.
# ------------------------------------------------------------------
D = {"dark": "dark", "light": "light", "night": "night"}

# ------------------------------------------------------------------
# Exact 33-consumer Night coverage declaration (design §5 matrix).
# ------------------------------------------------------------------
# ``night_artifact`` is the deterministic Night output path (relative to
# ROOT, POSIX separators) for repo-generation rows. Active-only matugen
# bridges carry an ``active:<path>`` marker because their Night delivery is
# the live ``colors.css``/``colors.rasi`` file, not a repository artifact.
# ``source`` records which sync branch owns the row (registry loop, explicit
# sync_repo_snippets() branch, or Herdr) and is the bijection-test hook.


class CoverageRow(NamedTuple):
    """One row of the 33-consumer Night coverage contract (design §5)."""

    consumer_id: str
    klass: str
    writer: str
    night_artifact: str
    selection_strategy: str
    source: str


COVERAGE: tuple[CoverageRow, ...] = (
    CoverageRow(
        "kitty",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; kitty_content",
        "DreamcoderKitty/.config/kitty/colors-dreamcoder-night.conf",
        "active symlink/file selects or receives Night",
        "registry",
    ),
    CoverageRow(
        "kitty_ui",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; kitty_ui_content",
        "DreamcoderKitty/.config/kitty/dreamcoder-ui-night.conf",
        "stable dreamcoder-ui.conf includes/contains Night",
        "registry",
    ),
    CoverageRow(
        "ghostty",
        "variant file + active-selected",
        "write_variant_files + update_ghostty_theme; ghostty_content",
        "DreamcoderGhostty/.config/ghostty/themes/dreamcoder-night",
        "select theme = dreamcoder-night",
        "registry",
    ),
    CoverageRow(
        "warp",
        "variant file + active-selected",
        "write_variant_files + update_warp_settings; warp_content",
        "DreamcoderWarp/.local/share/warp-terminal/themes/Dreamcoder-Night.yaml",
        "active symlink/file selects it; dark opacity/blur semantics",
        "registry",
    ),
    CoverageRow(
        "starship",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; starship_content",
        "DreamcoderShell/.config/starship-night.toml",
        "palette section never standard-dark ([palettes.dreamcoder-night])",
        "registry",
    ),
    CoverageRow(
        "codex_app",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; opencode_content",
        "DreamcoderCodexApp/Dreamcoder-Night.codex-theme.json",
        "stable Dreamcoder.codex-theme.json receives Night",
        "registry",
    ),
    CoverageRow(
        "codex_theme",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; codex_tmtheme_content",
        "DreamcoderCodexCLI/Dreamcoder-Night.tmTheme",
        "stable Dreamcoder.tmTheme receives Night",
        "registry",
    ),
    CoverageRow(
        "bat_theme",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; codex_tmtheme_content",
        "DreamcoderBat/.config/bat/themes/Dreamcoder-Night.tmTheme",
        "stable Dreamcoder.tmTheme receives Night",
        "registry",
    ),
    CoverageRow(
        "pi_theme",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; pi_theme_content",
        "DreamcoderPi/.pi/agent/themes/dreamcoder-night.json",
        "stable dreamcoder.json receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "antigravity",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; antigravity_content",
        "DreamcoderAntigravity/Dreamcoder-Night.json",
        "stable Dreamcoder.json receives Night; classified dark without name detection",
        "registry",
    ),
    CoverageRow(
        "tmux",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; tmux_content",
        "DreamcoderThemes/dreamcoder/tmux-dreamcoder-night.conf",
        "active file receives Night",
        "registry",
    ),
    CoverageRow(
        "lazygit",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; lazygit_content",
        "DreamcoderLazygit/.config/lazygit/config.night.yml",
        "live ~/.config/lazygit/config.yml symlink selects Night",
        "registry",
    ),
    CoverageRow(
        "zsh_syntax",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; zsh_syntax_content",
        "DreamcoderThemes/dreamcoder/zsh-syntax-highlighting-dreamcoder-night.zsh",
        "active sourced file receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "ls_colors",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; ls_colors_content",
        "DreamcoderThemes/dreamcoder/ls-colors-dreamcoder-night.sh",
        "active sourced file receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "bat",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; bat_content",
        "DreamcoderThemes/dreamcoder/bat-dreamcoder-night.sh",
        "selects the Night TextMate sibling (BAT_THEME=Dreamcoder-Night)",
        "registry",
    ),
    CoverageRow(
        "delta",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; delta_content",
        "DreamcoderThemes/dreamcoder/delta-dreamcoder-night.gitconfig",
        "active include/symlink selects Night; syntax-theme=Dreamcoder-Night",
        "registry",
    ),
    CoverageRow(
        "fzf",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; fzf_content",
        "DreamcoderThemes/dreamcoder/fzf-dreamcoder-night.sh",
        "active sourced file receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "btop",
        "variant file + active-selected",
        "write_variant_files + write_if_changed; btop_content",
        "DreamcoderThemes/dreamcoder/btop-dreamcoder-night.theme",
        "active dreamcoder.theme symlink selects Night",
        "registry",
    ),
    CoverageRow(
        "dunst",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; dunst_content",
        "DreamcoderThemes/dreamcoder/dunst-dreamcoder-night.conf",
        "active included file receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "firefox",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; firefox_content",
        "DreamcoderThemes/dreamcoder/firefox-dreamcoder-night.css",
        "active userChrome import receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "obsidian",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; obsidian_content",
        "DreamcoderThemes/dreamcoder/obsidian-dreamcoder-night.css",
        "active snippet receives/selects Night and keeps .theme-dark",
        "registry",
    ),
    CoverageRow(
        "cava",
        "snippet + active-selected",
        "write_variant_files + write_if_changed; cava_content",
        "DreamcoderThemes/dreamcoder/cava-dreamcoder-night.config",
        "active include receives/selects Night",
        "registry",
    ),
    CoverageRow(
        "opencode",
        "active-selected",
        "write_if_changed; opencode_content(transparent_background=True)",
        ".opencode/themes/dreamcoder.json",
        "stable theme ID dreamcoder overwritten with Night; no dreamcoder-night.json sibling",
        "explicit",
    ),
    CoverageRow(
        "zellij",
        "variant file + active-selected",
        "write_if_changed; zellij_content + update_zellij_config",
        "DreamcoderZellij/.config/zellij/dreamcoder-night.kdl",
        'generate KDL with themes { dreamcoder-night } and select theme "dreamcoder-night"',
        "explicit",
    ),
    CoverageRow(
        "nvim",
        "variant file + active-selected",
        "write_variant_files + nvim_dispatcher_content; nvim_content",
        "DreamcoderNvim/.config/nvim/colors/dreamcoder-night.lua",
        "dispatcher resolves DREAMCODER_THEME_PROFILE before base mode",
        "explicit",
    ),
    CoverageRow(
        "hyprland",
        "variant file + active-selected",
        "write_if_changed; hypr_content",
        "DreamcoderThemes/dreamcoder/hyprland-night.conf",
        "stable hyprland.conf receives Night; shell selector may point to the Night sibling",
        "explicit",
    ),
    CoverageRow(
        "hypr_colors_lua",
        "snippet + active-selected",
        "write_variant_files; hypr_colors_lua_content",
        "DreamcoderThemes/dreamcoder/hypr-colors-night.lua",
        "active symlink/file selects Night",
        "explicit",
    ),
    CoverageRow(
        "hypr_colors_conf",
        "snippet + active-selected",
        "write_variant_files; hypr_colors_conf_content",
        "DreamcoderThemes/dreamcoder/hypr-colors-night.conf",
        "active symlink/file selects Night",
        "explicit",
    ),
    CoverageRow(
        "waybar",
        "variant file + active-selected",
        "write_if_changed; waybar_content",
        "DreamcoderThemes/dreamcoder/waybar-night.css",
        "stable/selected Waybar CSS receives Night",
        "explicit",
    ),
    CoverageRow(
        "waybar_matugen",
        "snippet + active-selected",
        "write_if_changed; waybar_matugen_content",
        "active:waybar/colors.css",
        "write transformed Night directly; symlink-aware colors-night.css selection",
        "explicit",
    ),
    CoverageRow(
        "rofi",
        "variant file + active-selected",
        "write_if_changed; rofi_content",
        "DreamcoderThemes/dreamcoder/rofi-night.rasi",
        "stable/selected Rofi theme receives Night",
        "explicit",
    ),
    CoverageRow(
        "rofi_matugen",
        "snippet + active-selected",
        "write_if_changed; rofi_matugen_content",
        "active:rofi/colors.rasi",
        "write transformed Night directly; symlink-aware colors-night.rasi selection",
        "explicit",
    ),
    CoverageRow(
        "herdr",
        "variant file",
        "sync_herdr_repo_variants + write_if_changed; herdr_content",
        "DreamcoderHerdr/.config/herdr/dreamcoder/<version>/config.night.toml",
        "config.night.toml for every complete SUPPORTED_PROFILES entry; repository-only, no live activation",
        "herdr",
    ),
)


def validate_coverage_declaration(rows: tuple[CoverageRow, ...] = COVERAGE) -> list[str]:
    """Fail closed on missing, duplicate, or undeclared Night coverage.

    Internal consistency gate (R5): the registry loop and the explicit
    branches must each be represented by exactly one row, with no duplicate
    consumer IDs. The external bijection with the sync branches lives in
    the coverage test; this helper proves the declaration itself is well
    formed.
    """
    problems: list[str] = []
    ids = [row.consumer_id for row in rows]
    duplicates = sorted({cid for cid in ids if ids.count(cid) > 1})
    if duplicates:
        problems.append(f"duplicate coverage consumer ids: {duplicates}")
    if len(rows) != 33:
        problems.append(f"coverage declares {len(rows)} rows, expected exactly 33")

    registry_night = {
        (base / names["night"]).relative_to(ROOT).as_posix()
        for base, names, _builder, _active in VARIANT_REGISTRY
    }
    declared_registry = {row.night_artifact for row in rows if row.source == "registry"}
    missing = sorted(registry_night - declared_registry)
    extra = sorted(declared_registry - registry_night)
    if missing or extra:
        problems.append(f"registry coverage mismatch: undeclared={missing}, unregistered={extra}")

    declared_explicit = [row.consumer_id for row in rows if row.source == "explicit"]
    if len(declared_explicit) != 10:
        problems.append(f"explicit branch coverage has {len(declared_explicit)} rows, expected 10")
    herdr_rows = [row for row in rows if row.source == "herdr"]
    if len(herdr_rows) != 1:
        problems.append(f"herdr coverage has {len(herdr_rows)} rows, expected 1")
    return problems


VARIANT_REGISTRY: list[tuple[Path, dict[str, str], Callable[..., str], Path | None]] = [
    # -- Terminal targets --
    (
        ROOT / "DreamcoderKitty/.config/kitty",
        {k: f"colors-dreamcoder-{v}.conf" for k, v in D.items()},
        kitty_content,
        None,
    ),
    (
        ROOT / "DreamcoderKitty/.config/kitty",
        {k: f"dreamcoder-ui-{v}.conf" for k, v in D.items()},
        kitty_ui_content,
        None,
    ),
    (
        ROOT / "DreamcoderGhostty/.config/ghostty/themes",
        {k: f"dreamcoder-{v}" for k, v in D.items()},
        ghostty_content,
        None,
    ),
    (
        ROOT / "DreamcoderWarp/.local/share/warp-terminal/themes",
        {k: f"Dreamcoder-{v.title()}.yaml" for k, v in D.items()},
        warp_content,
        None,
    ),
    # -- Shell / prompt --
    (
        ROOT / "DreamcoderShell/.config",
        {k: f"starship-{v}.toml" for k, v in D.items()},
        starship_content,
        None,
    ),
    # -- TUI / editor themes --
    (
        ROOT / "DreamcoderCodexApp",
        {k: f"Dreamcoder-{v.title()}.codex-theme.json" for k, v in D.items()},
        opencode_content,
        ROOT / "DreamcoderCodexApp/Dreamcoder.codex-theme.json",
    ),
    (
        ROOT / "DreamcoderCodexCLI",
        {k: f"Dreamcoder-{v.title()}.tmTheme" for k, v in D.items()},
        codex_tmtheme_content,
        ROOT / "DreamcoderCodexCLI/Dreamcoder.tmTheme",
    ),
    (
        ROOT / "DreamcoderBat/.config/bat/themes",
        {k: f"Dreamcoder-{v.title()}.tmTheme" for k, v in D.items()},
        codex_tmtheme_content,
        ROOT / "DreamcoderBat/.config/bat/themes/Dreamcoder.tmTheme",
    ),
    # -- Pi CLI --
    (
        ROOT / "DreamcoderPi/.pi/agent/themes",
        {k: f"dreamcoder-{v}.json" for k, v in D.items()},
        pi_theme_content,
        ROOT / "DreamcoderPi/.pi/agent/themes/dreamcoder.json",
    ),
    # -- Antigravity --
    # active_path is None here: the unsuffixed Dreamcoder.json is pinned to
    # the Dark button palette (see the "Non-uniform entries" section below),
    # not the live active mode like other consumers' active files.
    (
        ROOT / "DreamcoderAntigravity",
        {k: f"Dreamcoder-{v.title()}.json" for k, v in D.items()},
        antigravity_content,
        None,
    ),
    # -- theme_dir entries (DreamcoderThemes/dreamcoder) --
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"zsh-syntax-highlighting-dreamcoder-{v}.zsh" for k, v in D.items()},
        zsh_syntax_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"ls-colors-dreamcoder-{v}.sh" for k, v in D.items()},
        ls_colors_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"bat-dreamcoder-{v}.sh" for k, v in D.items()},
        bat_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"delta-dreamcoder-{v}.gitconfig" for k, v in D.items()},
        delta_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"fzf-dreamcoder-{v}.sh" for k, v in D.items()},
        fzf_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"btop-dreamcoder-{v}.theme" for k, v in D.items()},
        btop_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"dunst-dreamcoder-{v}.conf" for k, v in D.items()},
        dunst_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"firefox-dreamcoder-{v}.css" for k, v in D.items()},
        firefox_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"obsidian-dreamcoder-{v}.css" for k, v in D.items()},
        obsidian_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"cava-dreamcoder-{v}.config" for k, v in D.items()},
        cava_content,
        None,
    ),
    (
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"tmux-dreamcoder-{v}.conf" for k, v in D.items()},
        tmux_content,
        None,
    ),
    (
        ROOT / "DreamcoderLazygit/.config/lazygit",
        {k: f"config.{v}.yml" for k, v in D.items()},
        lazygit_content,
        None,
    ),
]


def sync_herdr_repo_variants(
    variants: dict[str, dict[str, str]],
    profiles: tuple[HerdrProfile, ...] = SUPPORTED_PROFILES,
) -> list[bool]:
    """Generate managed repository variants for every supported profile.

    Repository variants only; never select or touch a live configuration.
    ``config.night.toml`` is emitted only when the caller supplies a night
    palette, so standard dark/light runs keep today's exact behavior (R5,
    design §5 row 32).
    """
    changes: list[bool] = []
    for profile in profiles:
        if profile is None or not profile.is_complete:
            continue
        base = ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder" / profile.evidence.version
        changes.append(
            write_if_changed(
                base / "config.dark.toml", herdr_content(profile, "dark", variants["dark"])
            )
        )
        changes.append(
            write_if_changed(
                base / "config.light.toml", herdr_content(profile, "light", variants["light"])
            )
        )
        if "night" in variants:
            changes.append(
                write_if_changed(
                    base / "config.night.toml", herdr_content(profile, "night", variants["night"])
                )
            )
    return changes


def write_active_repo_file(path: Path, content: str) -> bool:
    """write_if_changed for a repository-tracked "active" mirror.

    Unlike a live ~/.config target, this path must always be an
    independent file: an external mode selector, prior manual edit, or a
    stale artifact from an older sync can leave it as a symlink to one of
    its own -dark/-light/-night siblings, and write_if_changed follows
    symlinks — so writing the current active mode's content here would
    silently overwrite whichever sibling the symlink happened to point
    to (exactly the DreamcoderKitty/dreamcoder-ui.conf corruption fixed
    earlier). Unlink first so every active_path write in this module goes
    through the same guard instead of being patched one consumer at a
    time as each is discovered.
    """
    if path.is_symlink():
        path.unlink()
    return write_if_changed(path, content)


def sync_repo_snippets(variants: dict[str, dict[str, str]], active: dict[str, str]) -> list[bool]:
    repo_changes: list[bool] = []

    # ---- Declarative registry loop ----
    for base, names, builder, active_path in VARIANT_REGISTRY:
        repo_changes += write_variant_files(base, names, builder, variants)
        if active_path is not None:
            repo_changes.append(write_active_repo_file(active_path, builder(active)))

    # ---- Non-uniform entries (explicit calls) ----

    # Antigravity active file: button.background/foreground must always
    # resolve Dark's accent_2/on_accent (verify-theme-health.py
    # check_antigravity_files), independent of the currently active mode.
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderAntigravity/Dreamcoder.json",
            antigravity_content(variants["dark"]),
        )
    )

    # Kitty UI active file (variants handled by VARIANT_REGISTRY above).
    # This path can be left as a symlink to one of the -dark/-light/-night
    # siblings by an external mode selector; write_if_changed would follow
    # that symlink and overwrite the sibling's own content instead of this
    # file's, so unlink it first to guarantee an independent write target.
    kitty_ui_active_path = ROOT / "DreamcoderKitty/.config/kitty/dreamcoder-ui.conf"
    if kitty_ui_active_path.is_symlink():
        kitty_ui_active_path.unlink()
    repo_changes.append(write_active_repo_file(kitty_ui_active_path, kitty_ui_content(active)))

    # Opencode dotfile (transparent_background=True)
    repo_changes.append(
        write_active_repo_file(
            ROOT / ".opencode/themes/dreamcoder.json",
            opencode_content(active, transparent_background=True),
        )
    )

    # Hyprland — per-mode + active
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/hyprland-dark.conf",
            hypr_content(variants["dark"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/hyprland-light.conf",
            hypr_content(variants["light"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/hyprland-night.conf",
            hypr_content(variants["night"]),
        )
    )
    repo_changes += write_variant_files(
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"hypr-colors-{v}.lua" for k, v in D.items()},
        hypr_colors_lua_content,
        variants,
    )
    repo_changes += write_variant_files(
        ROOT / "DreamcoderThemes/dreamcoder",
        {k: f"hypr-colors-{v}.conf" for k, v in D.items()},
        hypr_colors_conf_content,
        variants,
    )

    # Waybar — per-mode + active
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/waybar-dark.css",
            waybar_content(variants["dark"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/waybar-light.css",
            waybar_content(variants["light"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/waybar-night.css",
            waybar_content(variants["night"]),
        )
    )

    # Rofi — per-mode + active
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/rofi-dark.rasi",
            rofi_content(variants["dark"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/rofi-light.rasi",
            rofi_content(variants["light"]),
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/rofi-night.rasi",
            rofi_content(variants["night"]),
        )
    )

    # Desktop/WM active files (no suffix — tracks current mode)
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/hyprland.conf", hypr_content(active)
        )
    )
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dreamcoder/waybar.css", waybar_content(active)
        )
    )
    repo_changes.append(
        write_active_repo_file(ROOT / "DreamcoderThemes/dreamcoder/rofi.rasi", rofi_content(active))
    )

    # Repo-root active files — the tracked copies users install to apps that
    # COPY the theme (firefox userChrome, obsidian, bat, delta, ...), as
    # opposed to the subdir actives above which symlinked desktop targets
    # consume. sync_active_targets writes the same paths from live config;
    # writing them here too keeps repo-only generation from leaving the two
    # active sets out of sync.
    repo_changes += [
        write_active_repo_file(
            ROOT / "DreamcoderThemes/zsh-syntax-highlighting-dreamcoder.zsh",
            zsh_syntax_content(active),
        ),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/ls-colors-dreamcoder.sh", ls_colors_content(active)
        ),
        write_active_repo_file(ROOT / "DreamcoderThemes/bat-dreamcoder.sh", bat_content(active)),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/delta-dreamcoder.gitconfig", delta_content(active)
        ),
        write_active_repo_file(ROOT / "DreamcoderThemes/fzf-dreamcoder.sh", fzf_content(active)),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/btop-dreamcoder.theme", btop_content(active)
        ),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/dunst-dreamcoder.conf", dunst_content(active)
        ),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/firefox-dreamcoder.css", firefox_content(active)
        ),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/obsidian-dreamcoder.css", obsidian_content(active)
        ),
        write_active_repo_file(
            ROOT / "DreamcoderThemes/cava-dreamcoder.config", cava_content(active)
        ),
        write_active_repo_file(ROOT / "DreamcoderThemes/hyprland.conf", hypr_content(active)),
        write_active_repo_file(ROOT / "DreamcoderThemes/waybar.css", waybar_content(active)),
        write_active_repo_file(ROOT / "DreamcoderThemes/rofi.rasi", rofi_content(active)),
        write_active_repo_file(
            ROOT / "DreamcoderLazygit/.config/lazygit/config.yml", lazygit_content(active)
        ),
    ]

    # Zellij — the consumed palette artifact is generated here (design §5
    # row 13); the active selector is patched by update_zellij_config.
    repo_changes.append(
        write_active_repo_file(
            ROOT / "DreamcoderZellij/.config/zellij/dreamcoder-night.kdl",
            zellij_content(variants["night"], "dreamcoder-night"),
        )
    )

    # Herdr repository variants are intentionally separate from live selection.
    repo_changes += sync_herdr_repo_variants(variants)

    # README
    repo_changes.append(
        write_active_repo_file(ROOT / "DreamcoderThemes/dreamcoder/README.md", readme_content())
    )

    # Nvim variant files
    nvim_dir = ROOT / "DreamcoderNvim/.config/nvim/colors"
    repo_changes += write_variant_files(
        nvim_dir,
        {k: f"dreamcoder-{v}.lua" for k, v in D.items()},
        nvim_content,
        variants,
    )

    return repo_changes


def sync_bat_theme_variants(paths: Any, variants: dict[str, dict[str, str]]) -> list[bool]:
    mode_names = {"dark": "dark", "light": "light"}
    return write_variant_files(
        paths.bat_theme_dir,
        {k: f"Dreamcoder-{v.title()}.tmTheme" for k, v in mode_names.items()},
        codex_tmtheme_content,
        variants,
    )


def print_summary(
    mode: str, paths: Any, changed: dict[str, bool], repo_changes: list[bool]
) -> None:
    print(f"Synced Dreamcoder {mode} identity")
    print(f"Kitty: {paths.kitty}")
    print(f"Kitty UI: {paths.kitty_ui}")
    print(f"Ghostty: {paths.ghostty}")
    print(f"Herdr repository variants: {paths.herdr_repo_variants}")
    print(f"Warp: {paths.warp}")
    print(f"opencode: {paths.opencode}")
    print(f"opencode tui: {paths.opencode_tui}")
    print(f"Codex CLI theme: {paths.codex_theme}")
    print(f"Bat theme dir: {paths.bat_theme_dir}")
    print(f"PI CLI theme: {paths.pi_theme}")
    print(f"PI CLI settings: {paths.pi_settings}")
    print(f"Starship: {paths.starship}")
    print(f"Lazygit: {paths.lazygit}")
    # New targets
    print(f"Neovim: {paths.nvim}")
    print(f"Zsh-syntax-highlighting: {paths.zsh_syntax}")
    print(f"LS_COLORS: {paths.ls_colors}")
    print(f"Bat: {paths.bat}")
    print(f"Delta: {paths.delta}")
    print(f"Fzf: {paths.fzf}")
    print(f"Btop: {paths.btop}")
    print(f"Dunst: {paths.dunst}")
    print(f"Firefox: {paths.firefox}")
    print(f"Obsidian: {paths.obsidian}")
    print(f"Cava: {paths.cava}")
    # Desktop/WM targets
    print(f"Hyprland: {paths.hyprland}")
    print(f"Hyprland colors.lua: {paths.hypr_colors_lua}")
    print(f"Hyprland colors.conf: {paths.hypr_colors_conf}")
    print(f"Waybar: {paths.waybar}")
    print(f"Waybar matugen: {paths.waybar_matugen}")
    print(f"Rofi: {paths.rofi}")
    print(f"Rofi matugen: {paths.rofi_matugen}")
    print("Changed: " + " ".join(f"{key}={flag}" for key, flag in changed.items()))
    print(f"Repo variant/snippet changes: {sum(repo_changes)}")


def _generation_profile() -> str:
    """Resolve the repo-generation render profile for this invocation.

    Task 4.3 replaced the Phase-3 env-only hook with the persisted
    ``render_profile()`` resolver: ``DREAMCODER_THEME_PROFILE`` (process-only,
    never mutates) -> persisted ``theme.render_profile`` -> schema default
    ``standard`` (design §3).
    """
    return render_profile()


def render_coverage_plan(
    paths: Any,
    active: dict[str, str],
    mode: str,
    profile: str,
    variants: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Render content for every one of the 32 coverage consumers in memory.

    Pure rendering: no writer, selector, or filesystem mutation (R5, ADR-004).
    This is the preparation boundary's in-memory 32-target render — the subject
    of the coverage assertion and the render-variant plan the activation
    transaction commits. Renderers still receive only ``dict[str, str]``.
    """
    plan: dict[str, str] = {
        "kitty": kitty_content(active),
        "kitty_ui": kitty_ui_content(active),
        "ghostty": ghostty_content(active),
        "warp": warp_content(active),
        "opencode": opencode_content(active, transparent_background=True),
        "codex_theme": codex_tmtheme_content(active),
        "bat_theme": codex_tmtheme_content(active),
        "pi_theme": pi_theme_content(active),
        "starship": starship_content(active),
        "tmux": tmux_content(active),
        "lazygit": lazygit_content(active),
        "nvim": nvim_dispatcher_content(),
        "zsh_syntax": zsh_syntax_content(active),
        "ls_colors": ls_colors_content(active),
        "bat": bat_content(active),
        "delta": delta_content(active),
        "fzf": fzf_content(active),
        "btop": btop_content(active),
        "dunst": dunst_content(active),
        "firefox": firefox_content(active),
        "obsidian": obsidian_content(active),
        "cava": cava_content(active),
        "hyprland": hypr_content(active),
        "hypr_colors_lua": hypr_colors_lua_content(active),
        "hypr_colors_conf": hypr_colors_conf_content(active),
        "waybar": waybar_content(active),
        "waybar_matugen": waybar_matugen_content(active),
        "rofi": rofi_content(active),
        "rofi_matugen": rofi_matugen_content(active),
        # Named-profile selector consumers (design §5 rows 13/6/10/32): the
        # selector line and the repo-only artifacts are rendered here too.
        "zellij": (
            'theme "dreamcoder-night"\n' if profile == "night" else f'theme "dreamcoder-{mode}"\n'
        ),
        "codex_app": opencode_content(variants["night"]),
        "antigravity": antigravity_content(variants["night"]),
    }
    complete = next((p for p in SUPPORTED_PROFILES if p is not None and p.is_complete), None)
    plan["herdr"] = herdr_content(complete, "night", variants["night"]) if complete else ""
    return plan


def prepare(base: str, profile: str) -> PreparedSync:
    """Validate-first preparation boundary (design §4, ADR-004; task 5.1).

    Loads canonical variants/guardrails/profile parameters, resolves the
    base+profile pair, adapts, transforms (Night), validates the final palette
    with the independent WCAG 2.2 + APCA dual gate, renders all 33 coverage
    consumers in memory, and asserts the coverage declaration — with ZERO
    filesystem writes. ``main()`` and the CLI activation transaction commit the
    returned immutable plan; a failed gate raises ``ThemeGateError`` before any
    writer, selector, or settings mutation (R4/R8).
    """
    if base not in {"light", "dark"}:
        raise SystemExit(f"base mode must be 'light' or 'dark' (got '{base}')")
    if profile not in VALID_RENDER_PROFILES:
        raise SystemExit(f"render profile must be 'standard' or 'night' (got '{profile}')")
    if profile == "night" and base != "dark":
        raise SystemExit(
            f"render profile 'night' requires base mode 'dark' (got '{base}'): "
            "Night always derives from the Dreamcoder Dark base (ADR-003)."
        )

    paths = theme_paths()
    guardrails = load_guardrails(paths.tokens_file)
    params = load_render_profile(paths.tokens_file)
    variants = load_variants(DEFAULT_VARIANTS, paths.tokens_file)
    # Night is a derived render variant (ADR-003): canonical dark + the
    # deterministic transform. Registry and explicit branches consume it through
    # the same dict[str, str] renderer shape (ADR-004).
    variants["night"] = night_palette(dict(variants["dark"]), params, guardrails)

    if profile == "night":
        adapted = adaptive_palette(variants["dark"], "dark", paths.wallpaper, adaptive_enabled())
        active = night_palette(adapted, params, guardrails)
    else:
        adapted = adaptive_palette(variants[base], base, paths.wallpaper, adaptive_enabled())
        active = adapted

    gate_errors = validate_palette(active, guardrails, profile=profile, mode=base)
    if gate_errors:
        raise ThemeGateError(gate_errors)

    coverage_problems = validate_coverage_declaration(COVERAGE)
    if coverage_problems:
        raise ThemeGateError(coverage_problems, kind="Coverage gate failed")

    render_plan = render_coverage_plan(paths, active, base, profile, variants)
    missing = [row.consumer_id for row in COVERAGE if row.consumer_id not in render_plan]
    if missing:
        raise ThemeGateError(
            [f"coverage consumer not rendered in preparation: {sorted(missing)}"],
            kind="Coverage gate failed",
        )

    return PreparedSync(
        mode=base,
        profile=profile,
        active=active,
        variants=variants,
        coverage=COVERAGE,
        render_plan=render_plan,
    )


def main() -> None:
    gen = ROOT / "scripts" / "generate-palette-tokens.py"
    if gen.is_file():
        subprocess.run([sys.executable, str(gen)], check=True)
    paths = theme_paths()
    profile = _generation_profile()
    # Night always resolves the Dreamcoder Dark base; otherwise the
    # Light/Dark base comes from theme_mode() (unchanged responsibility).
    base = "dark" if profile == "night" else theme_mode()

    # Validation-first preparation (R4, design §4): the final palette must pass
    # the independent WCAG 2.2 + APCA dual gate and the 33-consumer coverage
    # assertion BEFORE any writer or selector runs. A failed gate exits non-zero
    # with zero writes and no profile/settings mutation.
    try:
        prepared = prepare(base, profile)
    except ThemeGateError as exc:
        raise SystemExit(str(exc)) from None

    if profile == "night":
        # Repository-only Night generation: the 32-target coverage is produced
        # through sync_repo_snippets(); live active paths and the active bat
        # theme dir are left untouched (CLI activation owns them, Phase 5).
        repo_changes = (
            sync_repo_snippets(prepared.variants, prepared.active) if write_repo_enabled() else []
        )
        changed: dict[str, bool] = {}
        print_summary(prepared.mode, paths, changed, repo_changes)
        print("Night repository generation only — active outputs untouched (PR3)")
        return

    changed = sync_active_targets(paths, prepared.active, prepared.mode, prepared.profile)
    bat_variant_changes = sync_bat_theme_variants(paths, prepared.variants)
    repo_changes = (
        sync_repo_snippets(prepared.variants, prepared.active) if write_repo_enabled() else []
    )
    changed["bat_theme_variants"] = any(bat_variant_changes)

    if not valid_starship(paths.starship):
        raise SystemExit(f"Generated Starship config is invalid: {paths.starship}")
    print_summary(prepared.mode, paths, changed, repo_changes)

    # Best-effort, outside the 33-consumer coverage contract: Orca has no
    # Night profile of its own and lives entirely in the user's live
    # settings file, so a failure here must never abort the rest of sync.
    try:
        orca_status = sync_orca_theme(prepared.active)
    except OSError as exc:
        orca_status = f"skipped-error: {exc}"
    print(f"Orca terminal theme: {orca_status}")


if __name__ == "__main__":
    main()
