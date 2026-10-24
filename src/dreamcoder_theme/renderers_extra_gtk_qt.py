"""Pure canonical GTK named colors and legacy 21-role Qt6ct palettes.

No widget selectors, selection mutation or filesystem access.
Optional active consumers use reversible ownership; only Dark is rendered.
"""

from __future__ import annotations

from .renderer_contract import (
    ActiveStrategy,
    MutationStrategy,
    RendererRegistration,
    RendererStrategy,
    RepositoryStrategy,
    SyncDefinition,
)

# Includes every alias in Matugen's gtk-colors.css plus conventional GTK3
# theme aliases. Literal token values avoid depending on Matugen definitions.
_GTK_TOKENS = (
    ("accent_color", "accent"),
    ("accent_fg_color", "on_accent"),
    ("accent_bg_color", "accent"),
    ("window_bg_color", "surface0"),
    ("window_fg_color", "text"),
    ("headerbar_bg_color", "surface1"),
    ("headerbar_fg_color", "text"),
    ("popover_bg_color", "surface1"),
    ("popover_fg_color", "text"),
    ("view_bg_color", "bg"),
    ("view_fg_color", "text"),
    ("card_bg_color", "surface1"),
    ("card_fg_color", "text"),
    ("sidebar_bg_color", "surface0"),
    ("sidebar_fg_color", "text"),
    ("sidebar_border_color", "border_ui"),
    ("sidebar_backdrop_color", "surface0"),
    ("theme_bg_color", "surface0"),
    ("theme_fg_color", "text"),
    ("theme_base_color", "bg"),
    ("theme_text_color", "text"),
    ("theme_selected_bg_color", "accent"),
    ("theme_selected_fg_color", "on_accent"),
    ("theme_unfocused_bg_color", "surface0"),
    ("theme_unfocused_fg_color", "muted"),
    ("theme_unfocused_base_color", "bg"),
    ("theme_unfocused_text_color", "muted"),
    ("theme_unfocused_selected_bg_color", "selection_bg"),
    ("theme_unfocused_selected_fg_color", "selection_fg"),
    ("insensitive_bg_color", "surface1"),
    ("insensitive_fg_color", "disabled"),
    ("insensitive_base_color", "bg"),
    ("borders", "border_ui"),
    ("unfocused_borders", "border"),
    ("tooltip_bg_color", "surface1"),
    ("tooltip_fg_color", "text"),
    ("error_color", "error"),
    ("warning_color", "warning"),
    ("success_color", "success"),
)

# QPalette::ColorRole order from QtGui/qpalette.h. Keep NoRole at 17:
# qt6ct loadColorScheme maps ColorRole(i), not a list of visual roles.
# On Qt >= 6.6 qt6ct appends Highlight as Accent to these legacy 21 fields.
_QT_TOKENS = (
    ("WindowText", "text"),  # 0
    ("Button", "surface1"),  # 1
    ("Light", "surface3"),  # 2
    ("Midlight", "surface2"),  # 3
    ("Dark", "surface0"),  # 4
    ("Mid", "border"),  # 5
    ("Text", "text"),  # 6
    ("BrightText", "text_heading"),  # 7
    ("ButtonText", "text"),  # 8
    ("Base", "bg"),  # 9
    ("Window", "surface0"),  # 10
    ("Shadow", "bg"),  # 11
    ("Highlight", "accent"),  # 12
    ("HighlightedText", "on_accent"),  # 13
    ("Link", "link"),  # 14
    ("LinkVisited", "link_hover"),  # 15
    ("AlternateBase", "surface1"),  # 16
    ("NoRole", "bg"),  # 17
    ("ToolTipBase", "surface1"),  # 18
    ("ToolTipText", "text"),  # 19
    ("PlaceholderText", "subtle"),  # 20
)
_QT_GROUP_TEXT = frozenset({"WindowText", "Text", "ButtonText", "ToolTipText"})


def gtk_content(p: dict[str, str]) -> str:
    """Named colors only; import after Matugen and before user widget rules."""
    return "/* Dreamcoder Workbench canonical GTK colors */\n" + "".join(
        f"@define-color {role} {p[token]};\n" for role, token in _GTK_TOKENS
    )


def qt6ct_content(p: dict[str, str]) -> str:
    """Opaque ARGB fields in QPalette order for all three ColorScheme groups.

    Disabled text uses the canonical disabled token (4.5:1 minimum on Dark
    functional surfaces); disabled selection uses selection_bg rather than
    accent so its disabled foreground remains legible.
    """
    lines = ["# Dreamcoder Workbench canonical Qt6ct colors", "[ColorScheme]"]
    for group in ("active", "inactive", "disabled"):
        colors = []
        for role, default_token in _QT_TOKENS:
            token = default_token
            if group != "active" and role in _QT_GROUP_TEXT:
                token = "disabled" if group == "disabled" else "muted"
            if group == "disabled":
                if role in {"BrightText", "PlaceholderText", "HighlightedText"}:
                    token = "disabled"
                elif role == "Highlight":
                    token = "selection_bg"
            colors.append("#ff" + p[token].removeprefix("#").lower())
        lines.append(f"{group}_colors=" + ", ".join(colors))
    return "\n".join(lines) + "\n"


REGISTRATIONS = tuple(
    RendererRegistration(
        consumer_id=target,
        renderer=renderer,
        contract_version=1,
        modes=frozenset({"dark"}),
        output_kind="active",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.NO_VARIANTS,
            mutation=MutationStrategy.REVERSIBLE_OWNERSHIP,
        ),
        summary_label=f"{target} optional canonical Dark overlay",
    )
    for target, renderer in (("gtk3", gtk_content), ("gtk4", gtk_content), ("qt6ct", qt6ct_content))
)
