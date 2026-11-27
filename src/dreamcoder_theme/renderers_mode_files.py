"""Renderers for tracked per-mode colour files that used to be hand-copied.

``MODE_FILES`` is the table the sync walks for each mode; it sits outside the
36-consumer registry on purpose (those IDs are pinned by the coverage contract,
the byte-parity fixtures and the target manifest, none of which describe these
per-mode files). The renderers take the palette of the mode being written, so
Light and Dark share one implementation. The guards in
``tests/test_light_color_files.py`` and ``tests/test_dark_color_files.py`` tie
both together: a tracked file of a mode is in this table or holds only exact
tokens of that mode.

Every colour comes from the palette passed in, never from a literal.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import NamedTuple

from .palette import ansi
from .renderers_tmux import tmux_content
from .renderers_zellij import zellij_content

Palette = dict[str, str]


def alacritty_content(c: Palette) -> str:
    p = ansi(c)

    def table(name: str, colors: list[str]) -> str:
        rows = "\n".join(
            f'{key} = "{color}"'
            for key, color in zip(
                ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"),
                colors,
                strict=True,
            )
        )
        return f"[colors.{name}]\n{rows}\n"

    return f"""# {c["name"]} theme for Alacritty
# Auto-generated from tokens.json — do not edit manually

[colors.primary]
background = "{c["bg"]}"
foreground = "{c["text"]}"

[colors.cursor]
text = "{c["on_accent"]}"
cursor = "{c["accent"]}"

[colors.selection]
text = "{c["selection_fg"]}"
background = "{c["selection_bg"]}"

{table("normal", p[:8])}
{table("bright", p[8:])}"""


def wezterm_content(c: Palette) -> str:
    p = ansi(c)
    names = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")

    def palette_rows(colors: list[str]) -> str:
        return "\n".join(
            f'        "{color}",  -- {name}' for name, color in zip(names, colors, strict=True)
        )

    return f"""-- {c["name"]} theme for WezTerm
-- Auto-generated from tokens.json — do not edit manually

local M = {{}}

M.colors = {{
    foreground = "{c["text"]}",
    background = "{c["bg"]}",
    cursor_bg = "{c["accent"]}",
    cursor_fg = "{c["on_accent"]}",
    cursor_border = "{c["accent"]}",
    selection_bg = "{c["selection_bg"]}",
    selection_fg = "{c["selection_fg"]}",
    ansi = {{
{palette_rows(p[:8])}
    }},
    brights = {{
{palette_rows(p[8:])}
    }},
    tab_bar = {{
        background = "{c["bg_soft"]}",
        active_tab = {{
            bg_color = "{c["surface2"]}",
            fg_color = "{c["accent"]}",
        }},
        inactive_tab = {{
            bg_color = "{c["bg_soft"]}",
            fg_color = "{c["comment"]}",
        }},
        inactive_tab_hover = {{
            bg_color = "{c["surface2"]}",
            fg_color = "{c["accent"]}",
        }},
    }},
}}

return M
"""


def nushell_content(c: Palette) -> str:
    text = c["text"]
    return f"""# {c["name"]} theme for Nushell
# Auto-generated from tokens.json — do not edit manually

$env.config = {{
    color_config: {{
        separator: "{c["comment"]}"
        leading_trailing_space_bg: "{c["bg_soft"]}"
        header: "{c["accent"]}"
        date: "{text}"
        filesize: "{c["diagnostic"]}"
        row_index: "{c["comment"]}"
        bool: "{c["accent"]}"
        nothing: "{c["comment"]}"
        binary: "{text}"
        cellpath: "{text}"
        int: "{text}"
        duration: "{text}"
        range: "{text}"
        float: "{text}"
        string: "{text}"
        record: "{text}"
        list: "{text}"
        closure: "{text}"
        custom: "{text}"
    }}
    completions: {{
        case_sensitive: false
        quick: true
        partial: true
        algorithm: "fuzzy"
    }}
    history: {{
        max_size: 50000
        sync_on_enter: true
    }}
   rm: {{ always_trash: false }}
   ls: {{ use_ls_colors: true }}
}}
"""


def tmux_blocks_content(c: Palette) -> str:
    """The block-style tmux status theme (the text-only one is ``tmux_content``)."""
    return f"""# {c["name"]} theme for Tmux
# Auto-generated from tokens.json — do not edit manually

# ─── Colors ────────────────────────────────────────────
set -g status-style "bg={c["bg_soft"]},fg={c["text"]}"
set -g status-left "#[bg={c["accent"]},fg={c["on_accent"]},bold] #S #[bg={c["bg_soft"]},fg={c["accent"]}] "
set -g status-right "#[fg={c["diagnostic"]}]#[fg={c["text"]}] %H:%M #[fg={c["accent_2"]}]%Y-%m-%d "

# Window status
setw -g window-status-format "#[fg={c["comment"]}] #I:#W "
setw -g window-status-current-format "#[bg={c["surface2"]},fg={c["accent"]},bold] #I:#W "

# Pane borders
set -g pane-border-style "fg={c["surface2"]}"
set -g pane-active-border-style "fg={c["accent"]}"

# Messages
set -g message-style "bg={c["surface2"]},fg={c["text"]}"
set -g message-command-style "bg={c["surface2"]},fg={c["text"]}"

# Mode (copy mode highlight)
setw -g mode-style "bg={c["accent"]},fg={c["on_accent"]}"

# Bell
setw -g window-status-bell-style "bg={c["error"]},fg={c["on_error"]}"
"""


def tmux_ukiyo_content(c: Palette) -> str:
    """Kanagawa/ukiyo plugin colour options, sourced by apply-theme-mode.sh."""
    options = (
        ("text", c["text"]),
        ("bg-bar", c["bg_soft"]),
        ("bg-pane", c["bg"]),
        ("info", c["diagnostic"]),
        ("notice", c["accent_2"]),
        ("accent", c["accent"]),
        ("muted", c["muted"]),
        ("error", c["error"]),
        ("alert", c["warning"]),
        ("highlight", c["focus"]),
        ("selection", c["selection"]),
    )
    lines = "\n".join(f'set-option -g @ukiyo-color-{name} "{value}"' for name, value in options)
    return f"""# {c["name"]} — tmux ukiyo plugin colours
# Auto-generated from tokens.json — do not edit manually
# Sourced by scripts/apply-theme-mode.sh when the Kanagawa plugin is present.

{lines}
"""


def yazi_light_content(c: Palette) -> str:
    return f"""# {c["name"]} — Yazi theme
# Auto-generated from tokens.json — do not edit manually
# https://yazi-rs.github.io/docs/configuration/theme

[flavor]
dark = "dreamcoder-dark"
light = "dreamcoder-light"

[manager]
cwd = {{ fg = "{c["text"]}" }}

# Hovered
hovered = {{ fg = "{c["text"]}", bg = "{c["selection"]}" }}
preview_hovered = {{ fg = "{c["text"]}", bg = "{c["surface1"]}" }}

# Find
find_keyword = {{ fg = "{c["accent_2"]}", bold = true }}
find_position = {{ fg = "{c["diagnostic"]}" }}

# Marker
marker_copied = {{ fg = "{c["success"]}", bg = "{c["surface2"]}" }}
marker_cut = {{ fg = "{c["error"]}", bg = "{c["surface2"]}" }}
marker_selected = {{ fg = "{c["accent"]}", bg = "{c["surface2"]}" }}

# Tab
tab_active = {{ fg = "{c["text"]}", bg = "{c["bg"]}" }}
tab_inactive = {{ fg = "{c["comment"]}", bg = "{c["surface1"]}" }}
tab_width = 2

# Count
count_copied = {{ fg = "{c["on_accent"]}", bg = "{c["success"]}" }}
count_cut = {{ fg = "{c["on_error"]}", bg = "{c["error"]}" }}
count_selected = {{ fg = "{c["on_accent"]}", bg = "{c["accent"]}" }}

# Border
border_symbol = "│"
border_style = {{ fg = "{c["border"]}" }}

# Highlight
syntect_theme = "Dreamcoder-Light"

[status]
separator_open = ""
separator_close = ""
progress_label = {{ fg = "{c["text"]}", bold = true }}
progress_normal = {{ fg = "{c["accent"]}" }}
progress_error = {{ fg = "{c["error"]}" }}

# Permissions
permissions_t = {{ fg = "{c["diagnostic"]}" }}
permissions_r = {{ fg = "{c["success"]}" }}
permissions_w = {{ fg = "{c["accent_2"]}" }}
permissions_x = {{ fg = "{c["error"]}" }}
permissions_s = {{ fg = "{c["lavender"]}" }}

[input]
border = {{ fg = "{c["accent"]}" }}
title = {{}}
value = {{}}
selected = {{ bg = "{c["selection"]}" }}

[select]
border = {{ fg = "{c["accent"]}" }}
active = {{ fg = "{c["accent_2"]}" }}
inactive = {{}}

[tasks]
border = {{ fg = "{c["accent"]}" }}
title = {{}}
hovered = {{ fg = "{c["text"]}", bg = "{c["selection"]}" }}

[which]
mask = {{ bg = "{c["surface2"]}" }}
cand = {{ fg = "{c["diagnostic"]}" }}
rest = {{ fg = "{c["comment"]}" }}
desc = {{ fg = "{c["muted"]}" }}
separator = " ─ "
separator_style = {{ fg = "{c["border"]}" }}

[help]
on = {{ fg = "{c["accent"]}" }}
run = {{ fg = "{c["accent_2"]}" }}
desc = {{ fg = "{c["muted"]}" }}
hovered = {{ fg = "{c["text"]}", bg = "{c["selection"]}" }}
footer = {{ fg = "{c["comment"]}" }}
"""


_THEMES_BLOCK = re.compile(r"^themes \{\n.*?^\}\n", re.MULTILINE | re.DOTALL)


def zellij_config_content(c: Palette, theme_name: str, current: str) -> str:
    """Replace the ``themes { }`` block of a tracked mode config, keep the rest.

    The block holds the single ``theme_name`` theme rendered from the palette;
    any other embedded theme is dropped because the config selects one mode
    only. The splice is idempotent: a config that already holds the generated
    block comes back unchanged.
    """
    rendered = zellij_content(c, theme_name)
    block = rendered[rendered.index("themes {") :]
    if not _THEMES_BLOCK.search(current):
        raise ValueError(f"Zellij {theme_name} config has no top-level themes {{ }} block")
    return _THEMES_BLOCK.sub(lambda _m: block, current, count=1)


class ModeFile(NamedTuple):
    """One generated per-mode file: repository path and its renderer."""

    path: str
    renderer: Callable[[Palette], str]


MODE_FILES: dict[str, tuple[ModeFile, ...]] = {
    "light": (
        ModeFile("DreamcoderAlacritty/.config/alacritty/dreamcoder-light.toml", alacritty_content),
        ModeFile("DreamcoderWezTerm/.config/wezterm/dreamcoder-light.lua", wezterm_content),
        ModeFile("DreamcoderNushell/.config/nushell/dreamcoder-light.nu", nushell_content),
        # dreamcoder-theme.nu (what config.nu sources) is a tracked symlink to this
        # file, so it follows the generated Light theme; it needs no entry of its own.
        ModeFile("DreamcoderTmux/.config/tmux/dreamcoder-light.conf", tmux_blocks_content),
        # .tmux.conf sources the base file for every mode; the active-mode file
        # (tmux-dreamcoder.conf) overrides it once the mode is applied.
        ModeFile("DreamcoderTmux/.config/tmux/tmux-dreamcoder-base.conf", tmux_content),
        ModeFile("DreamcoderThemes/dreamcoder/tmux-ukiyo-light.conf", tmux_ukiyo_content),
        # Yazi has one theme.toml (flavor and syntect theme name Light).
        ModeFile("DreamcoderYazi/.config/yazi/theme.toml", yazi_light_content),
    ),
    "dark": (
        ModeFile("DreamcoderAlacritty/.config/alacritty/dreamcoder-dark.toml", alacritty_content),
        ModeFile("DreamcoderWezTerm/.config/wezterm/dreamcoder-dark.lua", wezterm_content),
        ModeFile("DreamcoderNushell/.config/nushell/dreamcoder-dark.nu", nushell_content),
        ModeFile("DreamcoderTmux/.config/tmux/dreamcoder-dark.conf", tmux_blocks_content),
        ModeFile("DreamcoderThemes/dreamcoder/tmux-ukiyo-dark.conf", tmux_ukiyo_content),
    ),
}

ZELLIJ_CONFIGS: dict[str, str] = {
    "light": "DreamcoderZellij/.config/zellij/config-light.kdl",
    "dark": "DreamcoderZellij/.config/zellij/config-dark.kdl",
}
