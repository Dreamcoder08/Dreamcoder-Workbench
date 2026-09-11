"""Focused extra Dreamcoder theme renderers."""

from __future__ import annotations

from .palette import detect_mode, mix


def obsidian_content(c: dict[str, str]) -> str:
    """Return an Obsidian CSS snippet with Dreamcoder colors."""
    mode = detect_mode(c)
    bg = c["bg"]

    is_dark = mode == "dark"
    class_prefix = ".theme-dark" if is_dark else ".theme-light"

    return f"""/* ========================================================
   {c["name"]} — Obsidian CSS snippet
   ========================================================
   Place in your vault's .obsidian/snippets/ folder.
   Enable in Settings → Appearance → CSS snippets. */

{class_prefix} {{
  /* Base — raw palette colors for backgrounds and surfaces */
  --background-primary: {c["bg"]};
  --background-primary-alt: {c["surface0"]};
  --background-secondary: {c["surface0"]};
  --background-secondary-alt: {c["surface1"]};
  --background-modifier-border: {c["border"]};
  --background-modifier-border-hover: {c["border_ui"]};
  --background-modifier-form-field: {c["surface0"]};
  --background-modifier-success: {mix(c["sage"], bg, 0.75)};
  --background-modifier-error: {mix(c["error"], bg, 0.75)};
  --background-modifier-message: {c["surface1"]};

  /* Text — guarded against background for accessibility */
  --text-normal: {c["text"]};
  --text-muted: {c["muted"]};
  --text-faint: {c["subtle"]};
  --text-accent: {c["accent"]};
  --text-accent-hover: {c["accent_2"]};
  --text-error: {c["error"]};
  --text-warning: {c["warning"]};
  --text-success: {c["success"]};
  --text-selection: {c["selection_bg"]};
  --text-on-accent: {c["on_accent"]};

  /* Interactive */
  --interactive-normal: {c["surface1"]};
  --interactive-hover: {c["hover"]};
  --interactive-accent: {c["accent"]};
  --interactive-accent-hover: {c["accent_2"]};
  --interactive-success: {c["success"]};

  /* Scrollbar */
  --scrollbar-bg: transparent;
  --scrollbar-thumb-bg: {c["border"]};
  --scrollbar-active-thumb-bg: {c["border_ui"]};

  /* Code — syntax highlighting colors */
  --code-normal: {c["text"]};
  --code-comment: {c["comment"]};
  --code-punctuation: {c["muted"]};
  --code-keyword: {c["accent"]};
  --code-operator: {c["accent_2"]};
  --code-function: {c["accent_2"]};
  --code-string: {c["sage"]};
  --code-number: {c["mauve"]};
  --code-tag: {c["accent"]};
  --code-important: {c["error"]};
  --code-background: {c["surface0"]};

  /* Heading */
  --h1-color: {c["text_heading"]};
  --h2-color: {c["text_heading"]};
  --h3-color: {c["accent_2"]};
  --h4-color: {c["diagnostic"]};
  --h5-color: {c["muted"]};
  --h6-color: {c["subtle"]};

  /* Link */
  --link-color: {c["link"]};
  --link-color-hover: {c["link_hover"]};
  --link-external-color: {c["info"]};
  --link-external-color-hover: {c["link_hover"]};

  /* Checkbox */
  --checkbox-color: {c["accent"]};
  --checkbox-color-hover: {c["accent_2"]};
  --checkbox-border-color: {c["border"]};
  --checkbox-mark-color: {c["bg"]};

  /* Table */
  --table-header-background: {c["surface1"]};
  --table-header-background-hover: {c["surface2"]};
  --table-row-background-hover: {c["surface0"]};
  --table-border-color: {c["border"]};

  /* Graph */
  --graph-line: {c["border"]};
  --graph-node: {c["muted"]};
  --graph-node-focused: {c["accent"]};
  --graph-node-tag: {c["diagnostic"]};
  --graph-node-attachment: {c["sage"]};
}}

/* Headings */
.markdown-rendered h1 {{ color: var(--h1-color); }}
.markdown-rendered h2 {{ color: var(--h2-color); }}
.markdown-rendered h3 {{ color: var(--h3-color); }}
.markdown-rendered h4 {{ color: var(--h4-color); }}
.markdown-rendered h5 {{ color: var(--h5-color); }}
.markdown-rendered h6 {{ color: var(--h6-color); }}

/* Tags */
.tag {{
  background-color: {mix(c["accent"], bg, 0.85)};
  color: {c["accent"]};
  border-radius: 4px;
  padding: 0 6px;
}}

/* Blockquotes */
blockquote {{
  border-color: {c["accent"]} !important;
}}

/* Search highlights */
.search-result-file-matched-text,
.is-selected .search-result-file-matched-text,
mark {{
  background-color: {mix(c["accent"], bg, 0.80)} !important;
  color: {c["text"]} !important;
}}

/* Active line in edit mode */
.cm-active {{
  background-color: {c["surface0"]} !important;
}}

/* Selection */
::selection {{
  background-color: {mix(c["surface1"], bg, 0.45)} !important;
}}

/* Tooltip */
.tooltip {{
  background-color: {c["surface1"]} !important;
  color: {c["text"]} !important;
}}

/* Menu */
.menu {{
  background-color: {c["surface0"]} !important;
}}

.menu-item:hover {{
  background-color: {c["surface1"]} !important;
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
        consumer_id="obsidian",
        renderer=obsidian_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Obsidian theme",
    ),
)
