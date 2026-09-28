"""Minimal Zellij KDL theme leaf writer (design §5 row 13).

Zellij consumes named theme artifacts through ``config.kdl``'s
``theme "dreamcoder-{mode}"`` selector. The generated KDL is the one palette
artifact sync.py produces for Zellij; the active selector is patched by
``update_zellij_config``.
"""

from __future__ import annotations


def zellij_content(c: dict[str, str], theme_name: str) -> str:
    """Render a Zellij KDL theme block from a palette dictionary.

    ``theme_name`` is the named theme key emitted inside ``themes { }`` (for
    example ``dreamcoder-dark``); colors are derived from the palette, never
    hand-tuned (ADR-004).
    """
    return f"""// {c.get("name", "Dreamcoder")} — Zellij theme ({theme_name})
// Auto-generated from tokens.json — do not edit manually

themes {{
    {theme_name} {{
        bg "{c["bg"]}"
        fg "{c["text"]}"
        black "{c["bg"]}"
        red "{c["error"]}"
        green "{c["sage"]}"
        yellow "{c["warning"]}"
        blue "{c["info"]}"
        magenta "{c["mauve"]}"
        cyan "{c["info"]}"
        white "{c["text"]}"
        orange "{c["warning"]}"
        gray "{c["muted"]}"

        // UI elements
        border "{c["border"]}"
        border_active "{c["accent"]}"
        border_unfocused "{c["border"]}"

        // Tab bar
        tab_bar_bg "{c["surface1"]}"
        tab_active_bg "{c["border"]}"
        tab_active_fg "{c["accent"]}"
        tab_inactive_bg "{c["surface1"]}"
        tab_inactive_fg "{c["muted"]}"

        // Pane frames
        pane_frame_bg "{c["surface1"]}"
        pane_frame_fg "{c["border"]}"

        // Selection
        selection_bg "{c["accent"]}"
        selection_fg "{c["bg"]}"
    }}
}}
"""


from .renderer_adapters import NamedZellijAdapter  # noqa: E402
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
        consumer_id="zellij",
        renderer=NamedZellijAdapter("dreamcoder"),
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.NAMED_ZELLIJ,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.PROFILE_AWARE_SELECTOR,
        ),
        summary_label="Zellij KDL theme",
    ),
)
