"""Focused extra Dreamcoder theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard, mix


def firefox_content(c: dict[str, str]) -> str:
    """Return a Firefox userChrome.css with Dreamcoder colors."""
    mode = detect_mode(c)
    bg = c["bg"]
    surface0 = c["surface0"]
    surface1 = c["surface1"]

    # Guard foreground/text colors against background
    txt = guard(c["text"], bg, mode)
    mtd = guard(c["muted"], bg, mode)
    acc = guard(c["accent"], bg, mode)
    acc2 = guard(c["accent_2"], bg, mode)

    # Background and UI colors - raw from palette
    hover_bg = mix(c["accent"], bg, 0.85)
    active_bg = mix(c["accent"], bg, 0.75)
    input_bg = surface0 if mode == "dark" else surface1
    toolbar_bg = surface0 if mode == "dark" else c["bg_soft"]

    return f"""/* ========================================================
   {c["name"]} — Firefox userChrome.css
   ========================================================
   Place in ~/.mozilla/firefox/*.default-release/chrome/userChrome.css
   Requires toolkit.legacyUserProfileCustomizations.stylesheets = true
   in about:config. */

:root {{
  --dreamcoder-bg: {bg};
  --dreamcoder-surface: {surface0};
  --dreamcoder-surface-1: {surface1};
  --dreamcoder-text: {txt};
  --dreamcoder-text-dim: {mtd};
  --dreamcoder-accent: {acc};
  --dreamcoder-accent-2: {acc2};
  --dreamcoder-border: {c["border"]};
  --dreamcoder-border-ui: {c["border_ui"]};
  --dreamcoder-error: {c["error"]};
  --dreamcoder-warning: {c["warning"]};
  --dreamcoder-sage: {c["sage"]};
  --dreamcoder-input-bg: {input_bg};
  --dreamcoder-toolbar-bg: {toolbar_bg};
  --dreamcoder-hover: {hover_bg};
  --dreamcoder-active: {active_bg};
}}

/* Main window */
#main-window,
#navigator-toolbox {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text) !important;
}}

/* Toolbar & URL bar */
#nav-bar,
#nav-bar toolbarbutton,
#urlbar,
#urlbar-background {{
  background-color: var(--dreamcoder-toolbar-bg) !important;
  color: var(--dreamcoder-text) !important;
  border-color: var(--dreamcoder-border) !important;
}}

#urlbar[focused="true"] > #urlbar-background {{
  border-color: var(--dreamcoder-accent) !important;
}}

/* Sidebar (bookmarks, history) */
#sidebar-box,
#sidebar {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text) !important;
}}

.sidebar-placesTreechildren {{
  color: var(--dreamcoder-text) !important;
}}

/* Tab bar */
#TabsToolbar,
#tabbrowser-tabs,
.tab-background {{
  background-color: var(--dreamcoder-bg) !important;
}}

.tabbrowser-tab:not([selected]) .tab-background {{
  background-color: var(--dreamcoder-surface) !important;
}}

.tabbrowser-tab[selected] .tab-background {{
  background-color: var(--dreamcoder-toolbar-bg) !important;
  border-color: var(--dreamcoder-accent) !important;
}}

.tabbrowser-tab .tab-label {{
  color: var(--dreamcoder-text-dim) !important;
}}

.tabbrowser-tab[selected] .tab-label {{
  color: var(--dreamcoder-text) !important;
}}

/* Context menus */
menupopup,
popup {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text) !important;
}}

menuitem {{
  color: var(--dreamcoder-text) !important;
}}

menuitem:hover {{
  background-color: var(--dreamcoder-hover) !important;
  color: var(--dreamcoder-text) !important;
}}

/* Status panel */
#statuspanel-label {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text-dim) !important;
  border-color: var(--dreamcoder-border) !important;
}}

/* Find bar */
#findbar {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text) !important;
}}

#findbar input {{
  background-color: var(--dreamcoder-input-bg) !important;
  color: var(--dreamcoder-text) !important;
  border-color: var(--dreamcoder-border) !important;
}}

/* Private browsing indicators */
#private-browsing-indicator-with-label {{
  color: var(--dreamcoder-accent-2) !important;
}}

/* Downloads panel */
#downloadsPanel,
#downloadsListBox {{
  background-color: var(--dreamcoder-bg) !important;
  color: var(--dreamcoder-text) !important;
}}

/* Scrollbar styling */
:root {{
  scrollbar-color: var(--dreamcoder-border) var(--dreamcoder-bg) !important;
}}

* {{
  scrollbar-width: thin !important;
  scrollbar-color: var(--dreamcoder-border) var(--dreamcoder-bg) !important;
}}
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
        consumer_id="firefox",
        renderer=firefox_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Firefox userChrome",
    ),
)
