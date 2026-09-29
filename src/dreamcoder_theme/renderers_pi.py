"""Focused CLI/editor theme renderers."""

from __future__ import annotations

import json

from .palette import detect_mode, make_guard, mix
from .renderers_opencode import opencode_tokens
from .settings import PI_THEME_SCHEMA


def pi_theme_content(c: dict[str, str]) -> str:
    t = opencode_tokens(c)
    mode_name = detect_mode(c)
    user_bg = mix(c["accent"], c["bg"], 0.96)
    pending_bg = mix(c["surface0"], c["bg"], 0.55)
    success_bg = mix(c["sage"], c["bg"], 0.82)
    error_bg = mix(c["error"], c["bg"], 0.84)
    theme = {
        "$schema": PI_THEME_SCHEMA,
        "name": "dreamcoder",
        "vars": {
            "cocoa": c["accent_2"],
            "lucuma": c["accent"],
            "diagnostic": c["diagnostic"],
            "sage": c["sage"],
            "mauve": c["mauve"],
            "coral": c["error"],
            "warning": c["warning"],
            "muted": c["muted"],
            "subtle": c["subtle"],
            "comment": c["comment"],
            "borderUi": c["border_ui"],
            "borderMuted": c["border"],
        },
        "colors": {
            "accent": "lucuma",
            "border": "borderUi",
            "borderAccent": "diagnostic",
            "borderMuted": "borderMuted",
            "success": "sage",
            "error": "coral",
            "warning": "warning",
            "muted": "muted",
            "dim": "subtle",
            "text": "",
            "thinkingText": "muted",
            "selectedBg": c["surface1"],
            "userMessageBg": user_bg,
            "userMessageText": "",
            "customMessageBg": c["surface0"],
            "customMessageText": "",
            "customMessageLabel": "lucuma",
            "toolPendingBg": pending_bg,
            "toolSuccessBg": success_bg,
            "toolErrorBg": error_bg,
            "toolTitle": "lucuma",
            "toolOutput": "",
            "mdHeading": "lucuma",
            "mdLink": "diagnostic",
            "mdLinkUrl": "muted",
            "mdCode": "sage",
            "mdCodeBlock": "",
            "mdCodeBlockBorder": "borderMuted",
            "mdQuote": "cocoa",
            "mdQuoteBorder": "borderMuted",
            "mdHr": "borderMuted",
            "mdListBullet": "lucuma",
            "toolDiffAdded": "sage",
            "toolDiffRemoved": "coral",
            "toolDiffContext": "muted",
            "syntaxComment": "comment",
            "syntaxKeyword": t["keyword"],
            "syntaxFunction": t["function"],
            "syntaxVariable": t["variable"],
            "syntaxString": t["string"],
            "syntaxNumber": t["number"],
            "syntaxType": t["type"],
            "syntaxOperator": t["operator"],
            "syntaxPunctuation": t["punctuation"],
            "thinkingOff": "comment",
            "thinkingMinimal": "borderUi",
            "thinkingLow": make_guard(c)(mix(c["diagnostic"], c["text"], 0.12)),
            "thinkingMedium": "diagnostic",
            "thinkingHigh": "mauve",
            "thinkingXhigh": "coral",
            "bashMode": "lucuma",
        },
    }
    return json.dumps(theme, indent=2) + "\n"


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
        consumer_id="pi_theme",
        renderer=pi_theme_content,
        contract_version=1,
        modes=frozenset({"dark", "light"}),
        output_kind="active-and-repository",
        sync=SyncDefinition(
            renderer=RendererStrategy.DIRECT_CONTENT,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.MODE_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="Pi agent theme",
    ),
)
