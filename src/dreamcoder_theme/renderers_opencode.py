"""Focused CLI/editor theme renderers."""

from __future__ import annotations

from .palette import detect_mode, guard, make_guard, mix, surface_guard


def opencode_tokens(c: dict[str, str]) -> dict[str, str]:
    g = make_guard(c, minimum=3.0)
    keyword = g(c["accent"])
    function = g(c["accent_2"])
    type_color = g(c["diagnostic"])
    constant = g(c["mauve"])
    sel_bg = c["selection_bg"]
    sel_fg = c["selection_fg"]
    return {
        "keyword": keyword,
        "function": function,
        "method": g(c["accent_2"]),
        "variable": g(c["muted"]),
        "parameter": g(mix(c["accent_2"], c["text"], 0.06)),
        "property": g(mix(c["diagnostic"], c["text"], 0.04)),
        "field": g(mix(c["sage"], c["text"], 0.05)),
        # Strings — lower guard for more vibrant green pop
        "string": make_guard(c, minimum=2.8)(c["sage"]),
        # Numbers — warm orange (further from keyword brown)
        "number": g(mix(c["accent"], c["mauve"], 0.45)),
        "constant": constant,
        "type": type_color,
        "constructor": g(mix(type_color, c["accent"], 0.18)),
        "enum": g(mix(type_color, c["sage"], 0.18)),
        "operator": g(c["accent_2"]),
        "punctuation": g(c["muted"]),
        "comment": make_guard(c, minimum=2.2)(c["comment"]),
        "todo": g(mix(c["warning"], c["text"], 0.12)),
        "deprecated": g(mix(c["error"], c["muted"], 0.28)),
        "code_bg": mix(c["border_ui"], c["bg"], 0.15),
        "selection": sel_bg,
        "selection_fg": sel_fg,  # text color on selection
        "search": mix(c["warning"], c["bg"], 0.42),
    }


def opencode_content(c: dict[str, str], transparent_background: bool = False) -> str:
    t = opencode_tokens(c)
    mode_name = detect_mode(c)

    # Mode-aware surface formulas
    if mode_name == "dark":
        panel_bg = c["surface1"]
        element_bg = c["surface1"]
        hover_bg = c["hover"]
        # Use a canonical surface tier that clears the distinct-surface guardrail.
        line_bg = c["surface1"]
        code_bg = c["surface1"]
        assistant_bg = mix(c["bg"], c["diagnostic"], 0.12)
        user_bg = mix(c["bg"], c["accent"], 0.12)
        tool_bg = mix(c["bg"], c["lavender"], 0.12)
        accent_muted = mix(c["accent"], c["bg"], 0.25)
        inline_code_bg = mix(c["sage"], c["border_ui"], 0.45)
        mix_base = c["border_ui"]
    else:
        panel_bg = c["surface0"]
        element_bg = mix(c["bg_soft"], c["surface1"], 0.4)
        hover_bg = c["hover"]
        line_bg = c["bg_soft"]
        # Light code_bg: use surface0 (near-bg) instead of surface1 for syntax contrast
        code_bg = c["surface0"]
        assistant_bg = mix(c["bg"], c["diagnostic"], 0.12)
        user_bg = mix(c["bg"], c["accent"], 0.15)
        tool_bg = mix(c["bg"], c["lavender"], 0.12)
        accent_muted = mix(c["accent"], c["bg"], 0.3)
        inline_code_bg = mix(c["sage"], c["bg"], 0.18)
        mix_base = c["bg"]

    diff_mix = 0.35 if mode_name == "dark" else 0.58
    added_bg = surface_guard(mix(c["sage"], mix_base, diff_mix), c["bg"], mode_name)
    removed_bg = surface_guard(mix(c["error"], mix_base, diff_mix), c["bg"], mode_name)
    hunk_bg = surface_guard(
        mix(c["lavender"], mix_base, 0.45 if mode_name == "dark" else 0.62),
        c["bg"],
        mode_name,
    )
    assistant = guard(mix(c["diagnostic"], c["text"], 0.18), c["bg"], mode_name)
    user = guard(mix(c["accent"], c["text"], 0.15), c["bg"], mode_name)
    background = "none" if transparent_background else c["bg"]
    return f"""{{
  "$schema": "https://opencode.ai/theme.json",
  "defs": {{
    "dreamBackground": "{c["bg"]}",
    "dreamPanel": "{c["surface0"]}",
    "dreamElement": "{c["bg_soft"]}",
    "dreamText": "{c["text"]}",
    "dreamMuted": "{c["muted"]}",
    "dreamCocoa": "{c["accent_2"]}",
    "dreamLucuma": "{c["accent"]}",
    "dreamDiagnostic": "{c["diagnostic"]}",
    "dreamSage": "{c["sage"]}",
    "dreamViolet": "{c["lavender"]}",
    "dreamMauve": "{c["mauve"]}",
    "dreamCoral": "{c["error"]}",
    "dreamWarning": "{c["warning"]}"
  }},
  "theme": {{
    "background": "{background}",
    "backgroundPanel": "{panel_bg}",
    "backgroundElement": "{element_bg}",
    "backgroundHover": "{hover_bg}",
    "backgroundSelected": "{t["selection"]}",
    "textSelected": "{t["selection_fg"]}",
    "backgroundCode": "{code_bg}",
    "backgroundSearch": "{t["search"]}",
    "backgroundLine": "{line_bg}",
    "backgroundAssistant": "{assistant_bg}",
    "backgroundUser": "{user_bg}",
    "backgroundTool": "{tool_bg}",
    "text": "{c["text"]}",
    "textMuted": "{c["muted"]}",
    "textSubtle": "{guard(c["subtle"], c["bg"], mode_name, minimum=5.5)}",
    "textPlaceholder": "{c["comment"]}",
    "textAssistant": "{assistant}",
    "textUser": "{user}",
    "textTool": "{t["type"]}",
    "primary": "{c["accent"]}",
    "secondary": "{c["accent_2"]}",
    "accent": "{c["accent"]}",
    "accentMuted": "{accent_muted}",
    "error": "{c["error"]}",
    "warning": "{c["warning"]}",
    "success": "{c["success"]}",
    "info": "{c["info"]}",
    "border": "{c["border_ui"]}",
    "borderActive": "{c["accent"]}",
    "borderSubtle": "{c["border"]}",
    "borderFocus": "{c["focus"]}",
    "shadow": "{mix(c["bg"], "#000000", 0.25)}",
    "diffAdded": "{c["sage"]}",
    "diffRemoved": "{c["error"]}",
    "diffContext": "{c["muted"]}",
    "diffHunkHeader": "{c["lavender"]}",
    "diffHighlightAdded": "{c["sage"]}",
    "diffHighlightRemoved": "{c["error"]}",
    "diffAddedBg": "{added_bg}",
    "diffRemovedBg": "{removed_bg}",
    "diffContextBg": "{background}",
    "diffLineNumber": "{c["subtle"]}",
    "diffAddedLineNumberBg": "{added_bg}",
    "diffRemovedLineNumberBg": "{removed_bg}",
    "diffHunkHeaderBg": "{hunk_bg}",
    "diffFold": "{c["comment"]}",
    "diffFoldBg": "{line_bg}",
    "markdownText": "{c["text"]}",
    "markdownHeading": "{c["accent"]}",
    "markdownLink": "{c["diagnostic"]}",
    "markdownLinkText": "{c["accent"]}",
    "markdownCode": "{c["sage"]}",
    "markdownBlockQuote": "{c["accent_2"]}",
    "markdownEmph": "{c["diagnostic"]}",
    "markdownStrong": "{c["accent"]}",
    "markdownHorizontalRule": "{c["border_ui"]}",
    "markdownListItem": "{c["accent"]}",
    "markdownListEnumeration": "{c["lavender"]}",
    "markdownTableBorder": "{c["border_ui"]}",
    "markdownTableHeader": "{c["accent_2"]}",
    "markdownImage": "{c["mauve"]}",
    "markdownImageText": "{c["text"]}",
    "markdownCodeBlock": "{c["text"]}",
    "markdownCodeBlockBg": "{code_bg}",
    "markdownInlineCodeBg": "{inline_code_bg}",
    "syntaxComment": "{t["comment"]}",
    "syntaxKeyword": "{t["keyword"]}",
    "syntaxFunction": "{t["function"]}",
    "syntaxMethod": "{t["method"]}",
    "syntaxVariable": "{t["variable"]}",
    "syntaxParameter": "{t["parameter"]}",
    "syntaxProperty": "{t["property"]}",
    "syntaxField": "{t["field"]}",
    "syntaxString": "{t["string"]}",
    "syntaxNumber": "{t["number"]}",
    "syntaxBoolean": "{t["constant"]}",
    "syntaxConstant": "{t["constant"]}",
    "syntaxType": "{t["type"]}",
    "syntaxClass": "{t["constructor"]}",
    "syntaxInterface": "{mix(t["type"], c["diagnostic"], 0.22)}",
    "syntaxEnum": "{t["enum"]}",
    "syntaxOperator": "{t["operator"]}",
    "syntaxPunctuation": "{t["punctuation"]}",
    "syntaxTag": "{t["keyword"]}",
    "syntaxAttribute": "{t["property"]}",
    "syntaxRegexp": "{mix(c["mauve"], c["error"], 0.28)}",
    "syntaxEscape": "{c["warning"]}",
    "syntaxNamespace": "{t["type"]}",
    "syntaxModule": "{t["type"]}",
    "syntaxDecorator": "{t["operator"]}",
    "syntaxBuiltin": "{t["constant"]}",
    "syntaxSpecial": "{c["warning"]}",
    "syntaxTodo": "{t["todo"]}",
    "syntaxDeprecated": "{t["deprecated"]}",
    "terminalBlack": "{guard(c["surface0"], c["bg"], mode_name)}",
    "terminalRed": "{c["error"]}",
    "terminalGreen": "{c["success"]}",
    "terminalYellow": "{c["warning"]}",
    "terminalBlue": "{c["info"]}",
    "terminalMagenta": "{c["mauve"]}",
    "terminalCyan": "{guard(mix(c["diagnostic"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalWhite": "{c["text"]}",
    "terminalBrightBlack": "{c["subtle"]}",
    "terminalBrightRed": "{guard(mix(c["error"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalBrightGreen": "{guard(mix(c["success"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalBrightYellow": "{guard(mix(c["warning"], c["text"], 0.16), c["bg"], mode_name)}",
    "terminalBrightBlue": "{guard(mix(c["info"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalBrightMagenta": "{guard(mix(c["mauve"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalBrightCyan": "{guard(mix(c["lavender"], c["text"], 0.18), c["bg"], mode_name)}",
    "terminalBrightWhite": "{c["text"]}"
  }}
}}
"""


from .renderer_adapters import TransparentOpenCodeAdapter  # noqa: E402
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
        consumer_id="opencode",
        renderer=TransparentOpenCodeAdapter(),
        contract_version=1,
        modes=frozenset({"dark", "light", "night"}),
        output_kind="active",
        sync=SyncDefinition(
            renderer=RendererStrategy.TRANSPARENT_OPENCODE,
            active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
            repository=RepositoryStrategy.NO_VARIANTS,
            mutation=MutationStrategy.SYMLINK_SAFE_ACTIVE_WRITE,
        ),
        summary_label="OpenCode transparent theme",
    ),
)
