"""Focused terminal and prompt theme renderers."""

from __future__ import annotations

from .palette import ansi, detect_mode


def kitty_content(c: dict[str, str]) -> str:
    p = ansi(c)
    sel_fg = c["selection_fg"]
    sel_bg = c["selection_bg"]
    return f"""# ==========================================================
#              {c["name"]}
# ==========================================================
# Color-only theme layer. Keep ML4W/Gentleman behavior elsewhere.

foreground              {c["text"]}
background              {c["bg"]}
selection_foreground    {sel_fg}
selection_background    {sel_bg}
url_color               {c["link"]}

cursor                  {c["accent"]}
cursor_text_color       {c["on_accent"]}
cursor_shape            block
cursor_blink_interval   0.5
cursor_stop_blinking_after 15.0

active_tab_foreground   {c["on_accent"]}
active_tab_background   {c["accent"]}
inactive_tab_foreground {c["muted"]}
inactive_tab_background {c["bg"]}
tab_bar_background      {c["bg"]}

active_border_color     {c["accent"]}
inactive_border_color   {c["border"]}
bell_border_color       {c["error"]}

color0  {p[0]}
color1  {p[1]}
color2  {p[2]}
color3  {p[3]}
color4  {p[4]}
color5  {p[5]}
color6  {p[6]}
color7  {p[7]}
color8  {p[8]}
color9  {p[9]}
color10 {p[10]}
color11 {p[11]}
color12 {p[12]}
color13 {p[13]}
color14 {p[14]}
color15 {p[15]}
color16 {c["accent_2"]}
color17 {c["error"]}

mark1_foreground        {c["on_accent"]}
mark1_background        {c["accent"]}
mark2_foreground        {c["on_accent"]}
mark2_background        {c["diagnostic"]}
mark3_foreground        {c["on_accent"]}
mark3_background        {c["mauve"]}
"""


def kitty_ui_content(c: dict[str, str]) -> str:
    is_dark = detect_mode(c) == "dark"
    opacity = "0.76" if is_dark else "0.96"
    blur = "24" if is_dark else "0"
    gamma = "1.0" if is_dark else "1.3"
    contrast = "15" if is_dark else "15"
    return f"""# Dreamcoder Kitty UI parity layer
# Loaded last so ML4W can keep behavior while Dreamcoder owns readability.
# Dark mode: glass blur (24px) with 76% opacity for depth.
# Light mode: opaque paper (96%) for maximum text legibility.
# text_composition_strategy:
#   gamma (1st val): thickness of dark text on light bg (default 1.0 on Linux).
#   contrast (2nd val): extra contrast %, 0-100 (default 0 on Linux).
#   Higher gamma = thicker text on light themes; contrast helps both modes.

font_family           JetBrainsMono Nerd Font
bold_font             auto
italic_font           auto
bold_italic_font      auto
font_size             14
disable_ligatures     cursor
symbol_map            U+E000-U+F8FF,U+F0000-U+10FFFF Symbols Nerd Font
box_drawing_scale     0.001, 1, 1.5, 2
# gamma {gamma} + {contrast}% contrast = thicker, sharper text matching Ghostty
text_composition_strategy {gamma} {contrast}
shell                 fish --login

window_padding_width  20 18 20 18
single_window_padding_width -1
placement_strategy    center
initial_window_width  1180
initial_window_height 780
background_opacity    {opacity}
dynamic_background_opacity no
background_blur       {blur}

tab_bar_edge          top
tab_bar_style         fade
tab_bar_min_tabs      2
tab_bar_margin_color  none
active_tab_font_style bold
inactive_tab_font_style normal

shell_integration     enabled no-cursor
mouse_hide_wait       2.0
copy_on_select        clipboard
dim_opacity           0.65
inactive_text_alpha   0.92

# Dreamcoder terminal shortcuts.
map ctrl+l            clear_terminal reset active
map ctrl+shift+l      clear_terminal scrollback active
map ctrl+backspace    send_text all \\x17
map ctrl+delete       send_text all \\ed

# Dreamcoder Motion: ML4W-inspired cursor trail, kept local and portable.
cursor_trail          1
"""


# --- Hexagonal-architecture-v2: adjacent immutable registrations (design §5) ---
from .renderer_contract import (  # noqa: E402
    ActiveStrategy,
    MutationStrategy,
    RendererRegistration,
    RendererStrategy,
    RepositoryStrategy,
    SyncDefinition,
)

REGISTRATIONS: tuple[RendererRegistration, ...] = (
    RendererRegistration(
        consumer_id="kitty",
        renderer=kitty_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Kitty terminal colors",
    ),
    RendererRegistration(
        consumer_id="kitty_ui",
        renderer=kitty_ui_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Kitty UI config",
    ),
)
