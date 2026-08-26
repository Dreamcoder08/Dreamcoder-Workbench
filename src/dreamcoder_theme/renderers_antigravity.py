"""Focused desktop shell theme renderers."""

from __future__ import annotations

import json


def antigravity_content(c: dict[str, str]) -> str:
    # Night must be classified dark WITHOUT depending on the word "Dark" in
    # the derived name (design §5 row 10): the transformed palette keeps
    # dark semantics in ``details``, which is the reliable signal.
    theme_type = "dark" if c.get("details", "darker") != "lighter" else "light"
    return json.dumps(
        {
            "name": c.get("name", "Dreamcoder"),
            "type": theme_type,
            "colors": {
                "editor.background": c["bg"],
                "editor.foreground": c["text"],
                "activityBar.background": c["surface0"],
                "activityBar.foreground": c["accent"],
                "activityBar.inactiveForeground": c["comment"],
                "activityBar.border": c["border_ui"],
                "sideBar.background": c["surface0"],
                "sideBar.foreground": c["text"],
                "sideBar.border": c["border_ui"],
                "statusBar.background": c["bg"],
                "statusBar.foreground": c["text"],
                "statusBar.border": c["border_ui"],
                "editorGroupHeader.tabsBackground": c["surface0"],
                "tab.activeBackground": c["bg"],
                "tab.activeForeground": c["accent"],
                "tab.inactiveBackground": c["surface0"],
                "tab.inactiveForeground": c["comment"],
                "tab.border": c["border_ui"],
                "editor.lineHighlightBackground": c["surface0"],
                "editorLineNumber.foreground": c["comment"],
                "editorLineNumber.activeForeground": c["accent"],
                "editorWidget.background": c["surface1"],
                "editorWidget.border": c["border_ui"],
                "input.background": c["surface1"],
                "input.foreground": c["text"],
                "input.border": c["focus"],
                "button.background": c["accent_2"],
                "button.foreground": c["on_accent"],
                "list.activeSelectionBackground": c["surface1"],
                "list.activeSelectionForeground": c["text"],
                "list.hoverBackground": c["surface0"],
                "editor.selectionBackground": c["surface1"],
                "terminal.background": c["bg"],
                "terminal.foreground": c["text"],
                "terminal.ansiBlack": c["surface0"],
                "terminal.ansiRed": c["error"],
                "terminal.ansiGreen": c["sage"],
                "terminal.ansiYellow": c["warning"],
                "terminal.ansiBlue": c["accent"],
                "terminal.ansiMagenta": c["mauve"],
                "terminal.ansiCyan": c["diagnostic"],
                "terminal.ansiWhite": c["text"],
            },
            "tokenColors": [
                {
                    "scope": ["comment", "punctuation.definition.comment"],
                    "settings": {"foreground": c["comment"], "fontStyle": "italic"},
                },
                {
                    "scope": [
                        "keyword",
                        "storage.type",
                        "storage.modifier",
                        "keyword.operator",
                    ],
                    "settings": {"foreground": c["accent"], "fontStyle": "bold"},
                },
                {
                    "scope": [
                        "entity.name.function",
                        "support.function",
                        "entity.name.method",
                    ],
                    "settings": {"foreground": c["diagnostic"]},
                },
                {
                    "scope": ["string", "punctuation.definition.string"],
                    "settings": {"foreground": c["sage"]},
                },
                {
                    "scope": ["constant.numeric", "constant.language"],
                    "settings": {"foreground": c["accent_2"]},
                },
                {
                    "scope": ["support.type", "entity.name.type", "entity.name.class"],
                    "settings": {"foreground": c["lavender"]},
                },
                {
                    "scope": ["variable", "meta.definition.variable"],
                    "settings": {"foreground": c["text"]},
                },
            ],
        },
        indent=2,
    )


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
        consumer_id="antigravity",
        renderer=antigravity_content,
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.WRITE_IF_CHANGED,
        ),
        summary_label="Antigravity JSON theme",
    ),
)
