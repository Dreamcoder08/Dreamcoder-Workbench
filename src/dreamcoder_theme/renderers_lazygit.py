"""Lazygit theme renderer for Dreamcoder.

Generates full ``config.yml`` files (active + ``config.{dark,light}.yml``
variants) from the canonical palette tokens. Non-color behavior is preserved
verbatim from the previous static config; only colors are derived from tokens,
so there is no duplicated per-mode hardcoded palette anywhere.
"""

from __future__ import annotations

from .palette import detect_mode


def _delta_syntax_theme(c: dict[str, str]) -> str:
    """Resolve the installed Catppuccin syntax theme for Delta inside Lazygit.

    The Dreamcoder ``*-light`` TextMate theme does not exist, so Lazygit's
    embedded Delta renderer must use installed valid Catppuccin themes:
    Latte for light and Mocha for dark.
    """
    return "Catppuccin Latte" if detect_mode(c) == "light" else "Catppuccin Mocha"


def lazygit_content(c: dict[str, str]) -> str:
    """Return a complete Lazygit ``config.yml`` for the given palette.

    The theme block, author colors, Delta syntax theme, and branch-log colors
    are derived from canonical tokens; every non-color option matches the
    established static config (file tree, tip, nerd fonts, panel layout,
    language, git behavior, update policy).
    """
    accent = c["accent"]
    accent_2 = c["accent_2"]
    border = c["border"]
    diagnostic = c["diagnostic"]
    error = c["error"]
    text = c["text"]
    selection = c["selection"]
    surface2 = c["surface2"]
    comment = c["comment"]
    bg = c["bg"]
    sage = c["sage"]
    lavender = c["lavender"]
    mauve = c["mauve"]
    author_colors = "\n".join(
        f'        "{color}": "{bg}"'
        for color in dict.fromkeys((accent, accent_2, diagnostic, sage, lavender, mauve))
    )

    return f"""# {c["name"]} — Lazygit theme
# https://github.com/jesseduffield/lazygit/blob/master/docs/Config.md

gui:
  theme:
    activeBorderColor:
      - "{accent}" # accent
      - "bold"
    inactiveBorderColor:
      - "{border}" # border
    searchingActiveBorderColor:
      - "{accent_2}" # accent-2
      - "bold"
    optionsTextColor:
      - "{diagnostic}" # diagnostic
    selectedLineBgColor:
      - "{selection}" # selection
    inactiveViewSelectedLineBgColor:
      - "{surface2}" # surface-2
    cherryPickedCommitFgColor:
      - "{diagnostic}"
    cherryPickedCommitBgColor:
      - "{accent_2}"
    markedBaseCommitFgColor:
      - "{diagnostic}"
    markedBaseCommitBgColor:
      - "{accent}"
    unstagedChangesColor:
      - "{error}" # error
    defaultFgColor:
      - "{text}" # text
  authorColors:
{author_colors}
  showFileTree: true
  showRandomTip: false
  nerdFontsVersion: "3"
  sidePanelWidth: 0.3
  expandFocusedSidePanel: true
  mainPanelSplitMode: "flexible"
  language: "en"
git:
  diffRenderers:
    - colorArg: always
      command: delta --syntax-theme "{_delta_syntax_theme(c)}" --paging=never
  merging:
    manualCommit: false
  skipHookPrefix: WIP
  autoFetch: true
  autoRefresh: true
  branchLogCmd: "git log --graph --pretty=format:'%C({accent})%h%Creset -%C({accent_2})%d%Creset %s %C({comment})(%cr) %C({diagnostic})<%an>%Creset' --date=relative"
update:
  method: never
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
        consumer_id="lazygit",
        renderer=lazygit_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Lazygit theme config",
    ),
)
