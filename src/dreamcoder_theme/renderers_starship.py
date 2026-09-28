"""Focused terminal and prompt theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard


def starship_content(c: dict[str, str]) -> str:
    mode = detect_mode(c)
    # Prompt surfaces are powerline segment backgrounds — need aesthetic
    # gradient, not text contrast. Use raw token values, not guard().
    prom_acc = guard(c["prompt_accent"], c["bg"], mode)
    prom_s0 = c["prompt_surface0"]  # segment bg, no guard
    prom_s1 = c["prompt_surface1"]  # segment bg, no guard
    prom_s2 = c["prompt_surface2"]  # segment bg, no guard
    prom_text = guard(c["prompt_text"], prom_s0, mode)  # text on darkest surface
    prom_muted = guard(c["prompt_muted"], c["bg"], mode)
    error = guard(c["error"], c["bg"], mode)
    warning = guard(c["warning"], c["bg"], mode)
    focus_col = c["focus"]
    diag = c["diagnostic"]
    lavender_col = c["lavender"]
    mauve_col = c["mauve"]
    palette_id = "dreamcoder"

    return f'''# ========================================================
# {c["name"]} — Starship prompt
# ========================================================
# Modern two-line layout with powerline segments.
# Line 1: context (directory, git), fill, cmd_duration, time
# Line 2: input character only (clean)
# Extra: status (exit code), AI session (hidden until active)

add_newline = true
palette = "{palette_id}"
command_timeout = 500

format = """
[\\uE0B6](fg:prompt_surface0)\\
$username\\
[\\uE0B0](bg:prompt_surface1 fg:prompt_surface0)\\
$directory\\
[\\uE0B0](bg:prompt_accent fg:prompt_surface1)\\
$git_branch\\
$git_status\\
[\\uE0B4](fg:prompt_accent)\\
$fill\\
$cmd_duration\\
$time
$character"""

right_format = ""

[palettes.{palette_id}]
bg = "{c["bg"]}"
text = "{c["text"]}"
muted = "{c["muted"]}"
prompt_bg = "{c["prompt_bg"]}"
prompt_surface0 = "{prom_s0}"
prompt_surface1 = "{prom_s1}"
prompt_surface2 = "{prom_s2}"
prompt_text = "{prom_text}"
prompt_muted = "{prom_muted}"
prompt_accent = "{prom_acc}"
prompt_accent_2 = "{c["prompt_accent_2"]}"
sage = "{c["sage"]}"
success = "{c["success"]}"
diagnostic = "{diag}"
info = "{c["info"]}"
lavender = "{lavender_col}"
mauve = "{mauve_col}"
error = "{error}"
warning = "{warning}"
border = "{c["border_ui"]}"
focus = "{focus_col}"
link = "{c["link"]}"

[username]
show_always = true
style_user = "bg:prompt_surface0 fg:prompt_text bold"
style_root = "bg:prompt_surface0 fg:error bold"
format = "[ \uf007 $user ]($style)"

[directory]
style = "bg:prompt_surface1 fg:prompt_text bold"
format = "[ $path ]($style)"
truncation_length = 2
truncate_to_repo = true
home_symbol = ""

[git_branch]
symbol = "\\uf418"
style = "bg:prompt_accent fg:prompt_bg bold"
format = "[ $symbol $branch ]($style)"

[git_status]
style = "bg:prompt_accent fg:prompt_bg bold"
format = "[$all_status$ahead_behind ]($style)"
conflicted = "\\ue727${{count}} "
ahead = "\\u21E1${{count}} "
behind = "\\u21E3${{count}} "
diverged = "\\u2195\\u21E1${{ahead_count}}\\u21E3${{behind_count}} "
untracked = "?${{count}} "
stashed = "\\uf0CF${{count}} "
modified = "~${{count}} "
staged = "+${{count}} "
renamed = "\\u00BB${{count}} "
deleted = "\\u2718${{count}} "

[status]
disabled = false
format = "[$symbol]($style)"
symbol = "\\u2717"
style = "bg:error fg:prompt_bg bold"
pipestatus = false

[fill]
symbol = " "

[cmd_duration]
min_time = 2500
style = "fg:prompt_muted"
format = "[  \\uf552 $duration ]($style)"

[time]
disabled = false
format = "[ $time ]($style)"
style = "fg:prompt_muted"

[character]
success_symbol = "[\\u276F](bold fg:prompt_accent)"
error_symbol = "[\\u276F](bold fg:error)"
vimcmd_symbol = "[\\u276E](bold fg:sage)"

# Runtime versions - show only when relevant, keep compact
[bun]
symbol = "\\uF5EF"
style = "fg:prompt_accent bold"
format = "[ $symbol $version]($style)"

[nodejs]
symbol = "\\uE718"
style = "fg:sage bold"
format = "[ $symbol $version]($style)"

[python]
symbol = "\\uE73C"
style = "fg:diag bold"
format = "[ $symbol $version]($style)"

[golang]
symbol = "\\uE627"
style = "fg:diag bold"
format = "[ $symbol $version]($style)"

[rust]
symbol = "\\uE7A8"
style = "fg:mauve bold"
format = "[ $symbol $version]($style)"

[custom.ai_session]
command = "cat ~/.cache/dreamcoder/ai-session.state 2>/dev/null || echo ''"
when = """test -f ~/.cache/dreamcoder/ai-session.state"""
format = "[\\uf5B5 $output]($style)"
style = "fg:diag bold"

[docker_context]
symbol = "\\uf308"
style = "fg:diag bold"
format = "[ $symbol $context]($style)"
only_with_files = true
'''


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
        consumer_id="starship",
        renderer=starship_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Starship prompt theme",
    ),
)
