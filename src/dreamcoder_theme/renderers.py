"""Public renderer exports — single flat import hub.

Every renderer function used by sync.py or other consumers is imported
directly from its leaf module. No intermediate passthrough registries.
"""

from .renderers_antigravity import antigravity_content
from .renderers_codex import codex_tmtheme_content
from .renderers_extra_bat_delta import bat_content, delta_content
from .renderers_extra_btop import btop_content
from .renderers_extra_firefox import firefox_content
from .renderers_extra_gtk_qt import gtk_content, qt6ct_content
from .renderers_extra_notify import cava_content, dunst_content
from .renderers_extra_nvim import nvim_content, nvim_dispatcher_content
from .renderers_extra_obsidian import obsidian_content
from .renderers_extra_shell import fzf_content, ls_colors_content, zsh_syntax_content
from .renderers_ghostty_warp import ghostty_content, warp_content
from .renderers_herdr import herdr_content
from .renderers_hypr_waybar_rofi import (
    hypr_colors_conf_content,
    hypr_colors_lua_content,
    hypr_content,
    rofi_content,
    rofi_matugen_content,
    waybar_content,
    waybar_matugen_content,
)
from .renderers_kitty import kitty_content, kitty_ui_content
from .renderers_lazygit import lazygit_content
from .renderers_opencode import opencode_content, opencode_tokens
from .renderers_pi import pi_theme_content
from .renderers_readme import readme_content
from .renderers_starship import starship_content
from .renderers_tmux import tmux_content
from .renderers_zellij import zellij_content

__all__ = [
    "antigravity_content",
    "bat_content",
    "btop_content",
    "cava_content",
    "codex_tmtheme_content",
    "delta_content",
    "dunst_content",
    "firefox_content",
    "fzf_content",
    "ghostty_content",
    "gtk_content",
    "herdr_content",
    "hypr_colors_conf_content",
    "hypr_colors_lua_content",
    "hypr_content",
    "kitty_content",
    "kitty_ui_content",
    "lazygit_content",
    "ls_colors_content",
    "nvim_content",
    "nvim_dispatcher_content",
    "obsidian_content",
    "opencode_content",
    "opencode_tokens",
    "pi_theme_content",
    "qt6ct_content",
    "readme_content",
    "rofi_content",
    "rofi_matugen_content",
    "starship_content",
    "tmux_content",
    "warp_content",
    "waybar_content",
    "waybar_matugen_content",
    "zellij_content",
    "zsh_syntax_content",
]
