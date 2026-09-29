"""Focused extra Dreamcoder theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard, mix


def dunst_content(c: dict[str, str]) -> str:
    """Return a Dunst config snippet with Dreamcoder colors."""
    mode = detect_mode(c)
    bg = c["bg"]
    # Guard foreground text against notification background
    txt = guard(c["text"], bg, mode)
    mtd = guard(c["muted"], bg, mode)
    acc = guard(c["accent"], bg, mode)
    err = guard(c["error"], bg, mode)
    # Background colors kept raw (notification backgrounds)
    urgent_bg = mix(c["error"], bg, 0.70)
    border = c["border"]
    border_ui = c["border_ui"]

    return f"""# ========================================================
# {c["name"]} — Dunst theme
# ========================================================
# Include from dunstrc:
#   [include] dreamcoder-dunst.conf

[urgency_low]
    background = "{c["bg"]}"
    foreground = "{txt}"
    highlight = "{acc}"
    frame_color = "{border}"

[urgency_normal]
    background = "{c["surface0"]}"
    foreground = "{txt}"
    highlight = "{acc}"
    frame_color = "{border_ui}"

[urgency_critical]
    background = "{urgent_bg}"
    foreground = "{txt}"
    highlight = "{err}"
    frame_color = "{err}"
"""


def cava_content(c: dict[str, str]) -> str:
    """Return a Cava config snippet with Dreamcoder colors."""
    mode = detect_mode(c)
    bg = c["bg"]

    return f"""# ========================================================
# {c["name"]} — Cava theme
# ========================================================
# Include from ~/.config/cava/config or place in
# ~/.config/cava/dreamcoder-cava.config.

[color]
# Background
background = '{c["bg"]}'

# Gradient mode for smooth transitions
gradient = 1
gradient_count = 8

# Gradient colors (low to high frequency) — raw palette, muted at lower end
gradient_color_1 = '{mix(c["diagnostic"], bg, 0.60)}'
gradient_color_2 = '{mix(c["diagnostic"], bg, 0.40)}'
gradient_color_3 = '{mix(c["accent"], bg, 0.50)}'
gradient_color_4 = '{mix(c["accent"], bg, 0.30)}'
gradient_color_5 = '{c["accent"]}'
gradient_color_6 = '{c["accent_2"]}'
gradient_color_7 = '{mix(c["error"], bg, 0.30)}'
gradient_color_8 = '{c["error"]}'

# Mono color (used when gradient = 0)
foreground = '{c["accent"]}'
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
        consumer_id="dunst",
        renderer=dunst_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Dunst notifications",
    ),
    RendererRegistration(
        consumer_id="cava",
        renderer=cava_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Cava visualizer",
    ),
)
