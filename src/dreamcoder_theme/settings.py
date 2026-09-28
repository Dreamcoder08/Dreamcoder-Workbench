"""Runtime configuration for Dreamcoder theme sync."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .settings_store import settings_get

ROOT = Path(__file__).resolve().parents[2]
PI_THEME_SCHEMA = (
    "https://raw.githubusercontent.com/earendil-works/pi/main/"
    "packages/coding-agent/src/modes/interactive/theme/theme-schema.json"
)


@dataclass(frozen=True)
class ThemePaths:
    kitty: Path
    kitty_config: Path
    kitty_ui: Path
    ghostty: Path
    ghostty_config: Path
    starship: Path
    tmux: Path
    lazygit: Path
    zellij_config: Path
    warp: Path
    warp_settings: Path
    opencode: Path
    opencode_tui: Path
    codex_theme: Path
    codex_config: Path
    pi_theme: Path
    pi_settings: Path
    wallpaper: Path
    tokens_file: Path
    # New targets
    bat_theme_dir: Path
    nvim: Path
    zsh_syntax: Path
    ls_colors: Path
    bat: Path
    delta: Path
    fzf: Path
    btop: Path
    dunst: Path
    firefox: Path
    obsidian: Path
    cava: Path
    # Desktop/WM targets
    hyprland: Path
    hypr_colors_lua: Path
    hypr_colors_conf: Path
    waybar: Path
    waybar_matugen: Path
    rofi: Path
    rofi_matugen: Path
    herdr_repo_variants: Path = field(
        default_factory=lambda: ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder"
    )
    herdr_managed_root: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "dreamcoder-herdr-managed"
    )
    herdr_selector: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "dreamcoder-herdr-selector.toml"
    )
    herdr_state: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "dreamcoder-herdr-state.json"
    )
    herdr_lock: Path = field(
        default_factory=lambda: Path(tempfile.gettempdir()) / "dreamcoder-herdr-activate.lock"
    )


def persisted_theme_mode() -> str | None:
    """Return the base mode apply-theme-mode.sh persisted, or None.

    ``~/.cache/dreamcoder/cursor-cli.env`` is the live mode record every
    mode switch writes (Neovim reads the same file as its fallback).
    """
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    try:
        lines = (cache_home / "dreamcoder" / "cursor-cli.env").read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        key, _, value = line.removeprefix("export ").partition("=")
        if key.strip() == "DREAMCODER_THEME_MODE":
            mode = value.strip().strip("\"'").lower()
            return mode if mode in {"dark", "light"} else None
    return None


def theme_mode() -> str:
    # Precedence: explicit env override, then the persisted live mode, then
    # Dreamcoder Dark as the repo default. Without the persisted fallback a
    # bare `dreamcoder sync` rendered Dark over a system running Light; a clean
    # env (CI, fresh shell) still never regenerates the legacy light palette.
    env_mode = os.environ.get("DREAMCODER_THEME_MODE")
    if env_mode is None:
        return persisted_theme_mode() or "dark"
    mode = env_mode.lower()
    if mode not in {"dark", "light"}:
        raise SystemExit("DREAMCODER_THEME_MODE must be 'dark' or 'light'")
    return mode


VALID_RENDER_PROFILES = frozenset({"standard", "night"})


def render_profile() -> str:
    """Resolve the effective rendering profile (design §3, R6).

    Precedence:
      1. ``DREAMCODER_THEME_PROFILE`` — process-only override for isolated
         generation and tests; it never mutates the persisted setting.
      2. Persisted ``settings_get("theme.render_profile")``.
      3. Schema default ``standard`` when absent.

    Invalid values fail closed instead of being interpreted as a runtime
    profile (R6 scenario "Invalid profile value is rejected").
    """
    env_profile = os.environ.get("DREAMCODER_THEME_PROFILE")
    if env_profile is not None:
        profile = env_profile.lower()
        if profile not in VALID_RENDER_PROFILES:
            raise SystemExit(
                f"DREAMCODER_THEME_PROFILE must be 'standard' or 'night' (got '{env_profile}')"
            )
        return profile
    persisted = settings_get("theme.render_profile")
    if persisted is not None:
        if not isinstance(persisted, str) or persisted not in VALID_RENDER_PROFILES:
            raise SystemExit(
                f"persisted theme.render_profile={persisted!r} is invalid; "
                "expected 'standard' or 'night'"
            )
        return persisted
    return "standard"


def effective_base_mode(mode: str | None = None, profile: str | None = None) -> str:
    """Resolve the base mode together with the render profile (ADR-003).

    Enforces ``profile == night -> mode == dark``: Night always derives from
    the Dreamcoder Dark base. A conflicting invocation such as
    ``DREAMCODER_THEME_MODE=light`` + ``DREAMCODER_THEME_PROFILE=night`` fails
    with an actionable error instead of choosing Dusk or silently coercing
    output (design §3). ``theme_mode()`` remains the Light/Dark base authority
    and never accepts Night as a base mode.
    """
    base = theme_mode() if mode is None else mode
    resolved_profile = render_profile() if profile is None else profile
    if resolved_profile == "night" and base != "dark":
        raise SystemExit(
            f"render profile 'night' requires base mode 'dark' (got '{base}'): "
            "Night always derives from the Dreamcoder Dark base; "
            "set DREAMCODER_THEME_MODE=dark or run the 'night' activation."
        )
    return base


def theme_paths() -> ThemePaths:
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    pi_agent_home = Path(os.environ.get("PI_AGENT_DIR", Path.home() / ".pi/agent"))
    dreamcoder_theme = ROOT / "DreamcoderThemes/dreamcoder"
    return ThemePaths(
        kitty=Path(os.environ.get("KITTY_COLORS", config_home / "kitty/colors-dreamcoder.conf")),
        kitty_config=Path(os.environ.get("KITTY_CONFIG", config_home / "kitty/kitty.conf")),
        kitty_ui=Path(
            os.environ.get("KITTY_DREAMCODER_UI", config_home / "kitty/dreamcoder-ui.conf")
        ),
        ghostty=Path(os.environ.get("GHOSTTY_THEME", config_home / "ghostty/themes/dreamcoder")),
        ghostty_config=Path(os.environ.get("GHOSTTY_CONFIG", config_home / "ghostty/config")),
        starship=Path(os.environ.get("STARSHIP_CONFIG", config_home / "starship.toml")),
        tmux=Path(os.environ.get("TMUX_THEME", config_home / "tmux/tmux-dreamcoder.conf")),
        lazygit=Path(
            os.environ.get(
                "DREAMCODER_LAZYGIT_THEME",
                ROOT / "DreamcoderLazygit/.config/lazygit/config.yml",
            )
        ),
        zellij_config=Path(os.environ.get("ZELLIJ_CONFIG", config_home / "zellij/config.kdl")),
        herdr_repo_variants=ROOT / "DreamcoderHerdr/.config/herdr/dreamcoder",
        herdr_managed_root=config_home / "herdr/dreamcoder/0.7.3",
        herdr_selector=config_home / "herdr/config.toml",
        herdr_state=config_home / "herdr/dreamcoder/state.json",
        herdr_lock=config_home / "herdr/dreamcoder/activate.lock",
        warp=Path(os.environ.get("WARP_THEME", data_home / "warp-terminal/themes/Dreamcoder.yaml")),
        warp_settings=Path(
            os.environ.get("WARP_SETTINGS", data_home / "warp-terminal/settings.toml")
        ),
        opencode=Path(
            os.environ.get("OPENCODE_THEME", config_home / "opencode/themes/dreamcoder.json")
        ),
        opencode_tui=Path(os.environ.get("OPENCODE_TUI", config_home / "opencode/tui.json")),
        codex_theme=Path(os.environ.get("CODEX_THEME", codex_home / "themes/Dreamcoder.tmTheme")),
        codex_config=Path(os.environ.get("CODEX_CONFIG", codex_home / "config.toml")),
        pi_theme=Path(os.environ.get("PI_THEME", pi_agent_home / "themes/dreamcoder.json")),
        pi_settings=Path(os.environ.get("PI_SETTINGS", pi_agent_home / "settings.json")),
        wallpaper=Path(os.environ.get("DREAMCODER_WALLPAPER", "")),
        tokens_file=Path(
            os.environ.get("DREAMCODER_TOKENS", ROOT / "DreamcoderThemes/dreamcoder/tokens.json")
        ),
        # New targets — all stored in themes/dreamcoder/ by default
        bat_theme_dir=Path(os.environ.get("BAT_THEME_DIR", config_home / "bat/themes")),
        nvim=Path(
            os.environ.get(
                "DREAMCODER_NVIM_THEME",
                dreamcoder_theme.parent.parent
                / "DreamcoderNvim/.config/nvim/colors/dreamcoder.lua",
            )
        ),
        zsh_syntax=Path(
            os.environ.get(
                "DREAMCODER_ZSH_SYNTAX_THEME",
                dreamcoder_theme.parent / "zsh-syntax-highlighting-dreamcoder.zsh",
            )
        ),
        ls_colors=Path(
            os.environ.get(
                "DREAMCODER_LS_COLORS_THEME",
                dreamcoder_theme.parent / "ls-colors-dreamcoder.sh",
            )
        ),
        bat=Path(
            os.environ.get("DREAMCODER_BAT_THEME", dreamcoder_theme.parent / "bat-dreamcoder.sh")
        ),
        delta=Path(
            os.environ.get(
                "DREAMCODER_DELTA_THEME",
                dreamcoder_theme.parent / "delta-dreamcoder.gitconfig",
            )
        ),
        fzf=Path(
            os.environ.get("DREAMCODER_FZF_THEME", dreamcoder_theme.parent / "fzf-dreamcoder.sh")
        ),
        btop=Path(
            os.environ.get(
                "DREAMCODER_BTOP_THEME", dreamcoder_theme.parent / "btop-dreamcoder.theme"
            )
        ),
        dunst=Path(
            os.environ.get(
                "DREAMCODER_DUNST_THEME", dreamcoder_theme.parent / "dunst-dreamcoder.conf"
            )
        ),
        firefox=Path(
            os.environ.get(
                "DREAMCODER_FIREFOX_THEME", dreamcoder_theme.parent / "firefox-dreamcoder.css"
            )
        ),
        obsidian=Path(
            os.environ.get(
                "DREAMCODER_OBSIDIAN_THEME",
                dreamcoder_theme.parent / "obsidian-dreamcoder.css",
            )
        ),
        cava=Path(
            os.environ.get(
                "DREAMCODER_CAVA_THEME", dreamcoder_theme.parent / "cava-dreamcoder.config"
            )
        ),
        # Desktop/WM targets
        hyprland=Path(
            os.environ.get(
                "DREAMCODER_HYPRLAND_THEME",
                dreamcoder_theme.parent / "hyprland.conf",
            )
        ),
        hypr_colors_lua=Path(
            os.environ.get(
                "DREAMCODER_HYPR_COLORS_LUA",
                config_home / "hypr/colors.lua",
            )
        ),
        hypr_colors_conf=Path(
            os.environ.get(
                "DREAMCODER_HYPR_COLORS_CONF",
                config_home / "hypr/colors.conf",
            )
        ),
        waybar=Path(
            os.environ.get(
                "DREAMCODER_WAYBAR_THEME",
                dreamcoder_theme.parent / "waybar.css",
            )
        ),
        waybar_matugen=Path(
            os.environ.get(
                "DREAMCODER_WAYBAR_MATUGEN",
                config_home / "waybar/colors.css",
            )
        ),
        rofi=Path(
            os.environ.get(
                "DREAMCODER_ROFI_THEME",
                dreamcoder_theme.parent / "rofi.rasi",
            )
        ),
        rofi_matugen=Path(
            os.environ.get(
                "DREAMCODER_ROFI_MATUGEN",
                config_home / "rofi/colors.rasi",
            )
        ),
    )


def adaptive_enabled() -> bool:
    return os.environ.get("DREAMCODER_ADAPTIVE", "1") != "0"


def write_repo_enabled() -> bool:
    return os.environ.get("DREAMCODER_WRITE_REPO", "1") != "0"
