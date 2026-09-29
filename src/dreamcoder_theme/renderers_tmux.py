"""tmux theme renderer for Dreamcoder."""

from __future__ import annotations

from .palette import detect_mode


def tmux_content(c: dict[str, str]) -> str:
    """Return a tmux config snippet using the Dreamcoder palette."""
    is_dark = detect_mode(c) == "dark"
    mode = "dark" if is_dark else "light"

    bg_pane = c["bg"]
    bg_bar = c["bg_soft"]
    text = c["text"]
    muted = c["muted"]
    accent = c["accent"]
    accent_2 = c["accent_2"]
    highlight = c["focus"] if is_dark else c["focus"]
    sel = c["surface1"]
    surface2 = c["surface2"]
    error = c["error"]
    success = c["success"]
    warn = c["warning"]
    info = c["diagnostic"]
    surface0 = c["surface0"]

    pane_fg = surface2
    pane_active_fg = highlight

    return rf"""# {c["name"]} — tmux {mode} theme
# Text-only minimal hierarchy: no blocks, no pills, no powerline.
# Source: tmux source-file ~/.config/tmux/tmux-dreamcoder-{mode}.conf

# Default terminal colours (truecolor)
set -g default-terminal "tmux-256color"
set -ga terminal-overrides ",*256col*:Tc"
set -ga terminal-overrides '*:Ss=\E[%p1%d q:Se=\E[2 q'

# Panes
set -g pane-border-style "fg={pane_fg},bg=default"
set -g pane-active-border-style "fg={pane_active_fg},bg=default"
set -g display-panes-colour "{accent}"
set -g display-panes-active-colour "{accent}"
# Semantic token for status integrations that report successful commands.
set -g @dreamcoder-success-colour "{success}"

# ─── Minimal status bar (text-only hierarchy) ─────────
set -g status-style "bg={bg_bar}"
set -g status-position top
set -g status-justify left
set -g status-interval 5
set -g status-left-length 60
set -g status-right-length 120

# Left: session name bold + middot separator
set -g status-left "#[fg={text},bold]  #S  #[fg={muted}]· "

# Window tabs — text-only, muted / accent active
set -g window-status-style "fg={muted}"
setw -g window-status-format "#I:#W "
set -g window-status-current-style "fg={accent},bold"
setw -g window-status-current-format "#I:#W "
setw -g window-status-separator ""

# Right: path muted + time bold
set -g status-right "#[fg={muted}]#{{b:pane_current_path}}  #[fg={text},bold]%H:%M  "

# Message
set -g message-style "fg={text},bg={surface0}"
set -g message-command-style "fg={text},bg={surface0}"

# Mode (copy mode)
setw -g mode-style "fg={bg_pane},bg={highlight}"

# Bell
setw -g window-status-bell-style "fg={bg_pane},bg={error},bold"
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
        consumer_id="tmux",
        renderer=tmux_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Tmux theme",
    ),
)
