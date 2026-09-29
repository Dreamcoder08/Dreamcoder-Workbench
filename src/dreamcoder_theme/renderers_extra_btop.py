"""Focused extra Dreamcoder theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard


def btop_content(c: dict[str, str]) -> str:
    """Return a Btop theme file."""
    mode = detect_mode(c)
    bg = c["bg"]
    # Guard foreground text colors; use raw palette for backgrounds/surfaces
    txt = guard(c["text"], bg, mode)
    mtd = guard(c["muted"], bg, mode)
    acc = guard(c["accent"], bg, mode)
    acc2 = guard(c["accent_2"], bg, mode)
    diag = guard(c["diagnostic"], bg, mode)
    sage = guard(c["sage"], bg, mode)
    lav = guard(c["lavender"], bg, mode)
    mauve = guard(c["mauve"], bg, mode)
    err = guard(c["error"], bg, mode)
    warn = guard(c["warning"], bg, mode)
    sel_bg = c["surface1"]

    return f"""# ========================================================
# {c["name"]} — Btop theme
# ========================================================
# Place in ~/.config/btop/themes/ and select from Btop UI.

theme[main_bg]="{c["bg"]}"
theme[main_fg]="{txt}"
theme[title]="{acc}"
theme[hi_fg]="{acc}"
theme[selected_bg]="{sel_bg}"
theme[selected_fg]="{txt}"
theme[inactive_fg]="{mtd}"
theme[graph_line]="{c["border"]}"
theme[proc_misc]="{mtd}"
theme[cpu_core]="{diag}"
theme[mem_free]="{sage}"
theme[mem_used]="{acc2}"
theme[mem_cached]="{diag}"
theme[user_bg]="{c["surface0"]}"
theme[user_fg]="{txt}"
theme[temp]="{warn}"
theme[disk]="{diag}"
theme[process]="{lav}"
theme[process_selected]="{acc}"
theme[core_bar]="{acc}"
theme[temp_bar]="{warn}"
theme[swap]="{mauve}"
theme[div_line]="{c["border"]}"
theme[process_bg]="{c["surface0"]}"
theme[process_fg]="{txt}"
theme[bad]="{err}"
theme[good]="{sage}"
theme[widget_bg]="{c["surface0"]}"
theme[widget_fg]="{txt}"
theme[widget_border]="{c["border"]}"
theme[widget_selected]="{acc}"
theme[graph_bg]="{c["surface0"]}"
theme[graph_fg]="{txt}"
theme[graph_high]="{acc2}"
theme[graph_low]="{diag}"
theme[graph_med]="{acc}"
theme[proc_bg]="{c["surface0"]}"
theme[proc_fg]="{txt}"
theme[process_border]="{c["border"]}"
theme[widget_title]="{acc}"
theme[box_border]="{c["border"]}"
theme[box_bg]="{c["surface0"]}"
theme[box_fg]="{txt}"
theme[box_selected]="{acc}"
theme[os_bg]="{c["surface0"]}"
theme[os_fg]="{txt}"
theme[clock_bg]="{c["surface0"]}"
theme[clock_fg]="{acc}"
theme[bat_high]="{sage}"
theme[bat_med]="{warn}"
theme[bat_low]="{err}"
theme[sensor_bg]="{c["surface0"]}"
theme[sensor_fg]="{txt}"
theme[sensor_bar_bg]="{c["surface1"]}"
theme[sensor_bar_fg]="{acc}"
theme[net_bg]="{c["surface0"]}"
theme[net_fg]="{txt}"
theme[net_download]="{sage}"
theme[net_upload]="{acc2}"
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
        consumer_id="btop",
        renderer=btop_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Btop theme",
    ),
)
