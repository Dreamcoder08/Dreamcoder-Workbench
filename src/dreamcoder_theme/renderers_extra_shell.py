"""Focused shell-theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard


def _fg(hex_color: str) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"38;2;{r};{g};{b}"


def _bg(hex_color: str) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"48;2;{r};{g};{b}"


def zsh_syntax_content(c: dict[str, str]) -> str:
    """Return a compact zsh-syntax-highlighting snippet."""
    mode, bg = detect_mode(c), c["bg"]

    def g(key: str) -> str:
        val = guard(c[key], bg, mode)
        assert val is not None
        return val

    pairs = {
        "default": f"fg={g('text')}",
        "unknown-token": f"fg={g('error')}",
        "reserved-word": f"fg={g('accent')},bold",
        "alias": f"fg={g('accent_2')}",
        "suffix-alias": f"fg={g('accent_2')}",
        "builtin": f"fg={g('accent')}",
        "function": f"fg={g('accent_2')}",
        "command": f"fg={g('accent')}",
        "precommand": f"fg={g('accent')},italic",
        "commandseparator": f"fg={g('muted')}",
        "hashed-command": f"fg={g('accent')}",
        "path": f"fg={g('diagnostic')}",
        "path_pathseparator": f"fg={g('accent')}",
        "path_prefix": f"fg={g('diagnostic')},underline",
        "path_approx": f"fg={g('warning')},underline",
        "globbing": f"fg={g('lavender')}",
        "history-expansion": f"fg={g('lavender')}",
        "single-hyphen-option": f"fg={g('diagnostic')}",
        "double-hyphen-option": f"fg={g('diagnostic')}",
        "back-quoted-argument": f"fg={g('sage')}",
        "single-quoted-argument": f"fg={g('sage')}",
        "double-quoted-argument": f"fg={g('sage')}",
        "dollar-quoted-argument": f"fg={g('sage')}",
        "rc-quote": f"fg={g('mauve')}",
        "dollar-double-quoted-argument": f"fg={g('mauve')}",
        "back-double-quoted-argument": f"fg={g('mauve')}",
        "back-dollar-quoted-argument": f"fg={g('mauve')}",
        "assign": f"fg={g('text')}",
        "redirection": f"fg={g('accent_2')}",
        "comment": f"fg={g('comment')},italic",
        "variable": f"fg={g('mauve')}",
        "mathvar": f"fg={g('mauve')}",
        "null": f"fg={g('muted')}",
        "bracket-level-1": f"fg={g('accent')}",
        "bracket-level-2": f"fg={g('diagnostic')}",
        "bracket-level-3": f"fg={g('sage')}",
        "bracket-level-4": f"fg={g('lavender')}",
        "cursor-matchingbracket": f"fg={bg},bg={g('accent')}",
    }
    assignments = [f"ZSH_HIGHLIGHT_STYLES[{key}]='{value}'" for key, value in pairs.items()]
    folded = ["; ".join(assignments[i : i + 4]) for i in range(0, len(assignments), 4)]
    body = "\n".join(folded)
    return f"# {c['name']} — zsh-syntax-highlighting\ntypeset -A ZSH_HIGHLIGHT_STYLES\n{body}\n"


def ls_colors_content(c: dict[str, str]) -> str:
    """Return a compact LS_COLORS/eza snippet."""
    mode, bg = detect_mode(c), c["bg"]

    def g(key: str) -> str:
        val = guard(c[key], bg, mode)
        assert val is not None
        return val

    common = {
        "di": _fg(g("accent")),
        "ex": _fg(g("accent_2")),
        "ln": _fg(g("diagnostic")),
        # Broken links invert onto the warning swatch: base bg text keeps AA.
        "or": f"{_bg(c['warning'])};{_fg(bg)}",
        "so": _fg(g("sage")),
        "pi": _fg(g("warning")),
        "bd": _fg(g("error")),
        "cd": _fg(g("error")),
        "su": f"{_bg(bg)};{_fg(g('accent_2'))}",
        "sg": f"{_bg(bg)};{_fg(g('accent_2'))}",
        "tw": f"{_fg(g('accent'))};{_bg(c['surface0'])}",
        "ow": f"{_fg(g('accent'))};{_bg(c['surface0'])}",
        "st": f"{_fg(g('accent'))};{_bg(c['surface0'])}",
    }
    groups = {
        _fg(g("lavender")): [
            "*.tar",
            "*.tgz",
            "*.gz",
            "*.bz2",
            "*.xz",
            "*.zst",
            "*.zip",
            "*.7z",
            "*.rar",
            "*.iso",
            "*.dmg",
        ],
        _fg(g("mauve")): [
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.bmp",
            "*.svg",
            "*.webp",
            "*.ico",
            "*.mp3",
            "*.wav",
            "*.flac",
            "*.ogg",
            "*.m4a",
            "*.mp4",
            "*.mkv",
            "*.webm",
            "*.mov",
        ],
        _fg(g("muted")): [
            "*.pdf",
            "*.doc",
            "*.docx",
            "*.odt",
            "*.xls",
            "*.xlsx",
            "*.ppt",
            "*.pptx",
            "*.txt",
            "*.cfg",
            "*.conf",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.toml",
            "*.xml",
            "*.css",
            "*.html",
            "*.c",
            "*.h",
            "*.cpp",
            "*.hpp",
            "*.swp",
            "*.swo",
            "*.bak",
            "*.orig",
        ],
        _fg(g("accent_2")): [
            "*.sh",
            "*.bash",
            "*.zsh",
            "*.fish",
            "*.py",
            "*.rb",
            "*.rs",
            "*.go",
            "*.ts",
            "*.js",
        ],
        g("accent"): ["*.md"],
    }
    entries = [f"{key}={value}" for key, value in common.items()]
    entries += [f"{pattern}={style}" for style, patterns in groups.items() for pattern in patterns]
    eza = {
        "di": common["di"],
        "ex": common["ex"],
        "ln": common["ln"],
        "so": common["so"],
        "pi": common["pi"],
        "bd": common["bd"],
        "cd": common["cd"],
        "uw": _fg(g("warning")),
        "ux": _fg(g("error")),
        "gwx": _fg(g("warning")),
        "*.md": g("accent"),
    }
    return f"#!/usr/bin/env bash\nset -euo pipefail\n# {c['name']} — LS_COLORS / eza\nexport LS_COLORS='{':'.join(entries)}'\nexport EZA_COLORS='{':'.join(f'{k}={v}' for k, v in eza.items())}'\n"


def fzf_content(c: dict[str, str]) -> str:
    """Return a compact FZF_DEFAULT_OPTS export."""
    fg = guard(c["text"], c["bg"], detect_mode(c))
    mode = detect_mode(c)
    # In dark mode, use surface1 for selected/preview backgrounds (visible)
    bg_plus = c["surface1"] if mode == "dark" else c["surface0"]
    gutter_bg = c["surface1"] if mode == "dark" else c["bg"]
    preview_bg = c["surface1"] if mode == "dark" else c["bg"]
    parts = [
        f"bg:{c['bg']}",
        f"bg+:{bg_plus}",
        f"fg:{fg}",
        f"fg+:{fg}",
        f"hl:{c['accent']}",
        f"hl+:{c['accent']}",
        f"info:{c['diagnostic']}",
        f"marker:{c['sage']}",
        f"prompt:{c['accent']}",
        f"spinner:{c['lavender']}",
        f"pointer:{c['accent_2']}",
        f"header:{c['muted']}",
        f"border:{c['border']}",
        f"label:{c['muted']}",
        f"query:{fg}",
        f"gutter:{gutter_bg}",
        f"scrollbar:{c['border']}",
        f"separator:{c['border']}",
        f"preview-bg:{preview_bg}",
        f"preview-border:{c['border']}",
    ]
    return f'#!/usr/bin/env bash\nset -euo pipefail\n# {c["name"]} — fzf\nexport FZF_DEFAULT_OPTS="${{FZF_DEFAULT_OPTS:-}} --color={",".join(parts)}"\n'


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
        consumer_id="zsh_syntax",
        renderer=zsh_syntax_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Zsh syntax highlighting",
    ),
    RendererRegistration(
        consumer_id="ls_colors",
        renderer=ls_colors_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="LS_COLORS snippet",
    ),
    RendererRegistration(
        consumer_id="fzf",
        renderer=fzf_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Fzf snippet",
    ),
)
