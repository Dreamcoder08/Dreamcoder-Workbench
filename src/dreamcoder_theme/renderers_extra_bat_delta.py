"""Focused extra Dreamcoder theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard, mix


def bat_content(c: dict[str, str]) -> str:
    """Return a Bat theme config snippet with modern defaults."""
    mode_name = detect_mode(c)
    # The Night snippet selects the Night TextMate sibling (design §5 row
    # 17): the derived palette name is the deterministic profile signal
    # because the format embeds the theme name.
    theme = f"Dreamcoder-{'Night' if 'Night' in c.get('name', '') else mode_name.title()}"
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"# {c['name']} — Bat theme; run 'bat cache --build' after installing the tmTheme.\n"
        f'export BAT_THEME="{theme}"\n'
        'export BAT_STYLE="auto,changes,header,grid"\n'
        'export BAT_PAGER="less -RF"\n'
        'export BAT_TABS="4"\n'
    )


def delta_content(c: dict[str, str]) -> str:
    """Return a Git Delta config snippet with Dreamcoder colors."""
    mode = detect_mode(c)
    bg = c["bg"]

    def g(color: str) -> str:
        return guard(c[color], bg, mode)

    # Mode-aware diff backgrounds: surface1 base visible in both modes
    if mode == "dark":
        plus_bg = mix(c["sage"], c["surface1"], 0.45)
        minus_bg = mix(c["error"], c["surface1"], 0.45)
        hunk_bg = mix(c["muted"], c["surface1"], 0.35)
    else:
        plus_bg = mix(c["sage"], bg, 0.85)
        minus_bg = mix(c["error"], bg, 0.85)
        hunk_bg = mix(c["muted"], bg, 0.85)

    # Syntax highlighting theme: the Night snippet selects the Night
    # TextMate sibling (design §5 row 18) — the format embeds the name.
    syntax_theme = (
        "Dreamcoder-Night" if "Night" in c.get("name", "") else f"Dreamcoder-{mode.title()}"
    )

    return f"""# ========================================================
# {c["name"]} — Git Delta theme
# ========================================================
# Include from ~/.config/git/config:
#   [include]
#       path = ~/.config/git/delta-dreamcoder.gitconfig

[delta]
    # Syntax highlighting theme for diff content
    syntax-theme = {syntax_theme}

    # Line colors
    plus-color = "{plus_bg}"
    minus-color = "{minus_bg}"
    plus-emph-color = "{g("sage")}"
    minus-emph-color = "{g("error")}"

    # Diff UI
    file-style = "{g("accent")}"
    file-decoration-style = "bold yellow box ul"
    hunk-header-style = "file line-number syntax"
    hunk-header-decoration-style = "yellow box"
    hunk-header-file-style = "{g("accent")}"
    hunk-header-line-number-style = "{g("muted")}"
    hunk-header-color = "{hunk_bg}"

    # Commit decorations
    commit-style = "{g("accent")} bold"
    commit-decoration-style = "bold yellow box ul"

    # Line numbers
    line-numbers = true
    line-numbers-left-style = "{g("muted")}"
    line-numbers-right-style = "{g("muted")}"
    line-numbers-minus-style = "{g("error")}"
    line-numbers-plus-style = "{g("sage")}"

    # Side-by-side
    side-by-side = true

    # Whitespace highlighting
    whitespace-error-style = "{g("warning")}"

    # Navigation
    navigate = true
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
        consumer_id="bat",
        renderer=bat_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Bat snippet",
    ),
    RendererRegistration(
        consumer_id="delta",
        renderer=delta_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Delta gitconfig snippet",
    ),
)
