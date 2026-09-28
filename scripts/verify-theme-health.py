#!/usr/bin/env python3
import importlib.util
import json
import plistlib
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme._math import apca_lc, contrast  # noqa: E402
from dreamcoder_theme.design_system import (  # noqa: E402
    evaluate_contract,
    load_contract,
    load_tokens,
)
from dreamcoder_theme.palette import ansi as terminal_ansi  # noqa: E402
from dreamcoder_theme.palette import validate_palette  # noqa: E402
from dreamcoder_theme.renderers_opencode import opencode_content  # noqa: E402

FILES = [
    ROOT / "DreamcoderCodexApp/Dreamcoder.codex-theme.json",
    ROOT / "DreamcoderCodexApp/Dreamcoder-Light.codex-theme.json",
    ROOT / "DreamcoderCodexApp/Dreamcoder-Dark.codex-theme.json",
]
ANTIGRAVITY_FILES = [
    ROOT / "DreamcoderAntigravity/Dreamcoder.json",
    ROOT / "DreamcoderAntigravity/Dreamcoder-Dark.json",
    ROOT / "DreamcoderAntigravity/Dreamcoder-Light.json",
]
TOKEN_FILE = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
TOKENS_SCHEMA_FILE = ROOT / "DreamcoderThemes/dreamcoder/tokens.schema.json"
OPENCODE_THEME_DIR = ROOT / ".opencode/themes"
DESIGN_SYSTEM_CONTRACT_FILE = ROOT / "DreamcoderThemes/dreamcoder/design-system.json"
DESIGN_SYSTEM_SCHEMA_FILE = ROOT / "DreamcoderThemes/dreamcoder/design-system.schema.json"
GENERATOR_FILE = ROOT / "scripts/generate-palette-tokens.py"
CODEX_CLI_FILES = [
    ROOT / "DreamcoderCodexCLI/Dreamcoder.tmTheme",
    ROOT / "DreamcoderCodexCLI/Dreamcoder-Light.tmTheme",
    ROOT / "DreamcoderCodexCLI/Dreamcoder-Dark.tmTheme",
]
KITTY_FILES = [
    ROOT / "DreamcoderKitty" / ".config" / "kitty" / "colors-dreamcoder-dark.conf",
    ROOT / "DreamcoderKitty" / ".config" / "kitty" / "colors-dreamcoder-light.conf",
]
STARSHIP_FILES = [
    ROOT / "DreamcoderShell" / ".config" / "starship-dark.toml",
    ROOT / "DreamcoderShell" / ".config" / "starship-light.toml",
]
GHOSTTY_FILES = [
    ROOT / "DreamcoderGhostty" / ".config" / "ghostty" / "themes" / "dreamcoder-dark",
    ROOT / "DreamcoderGhostty" / ".config" / "ghostty" / "themes" / "dreamcoder-light",
]
WAYBAR_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "waybar-dark.css",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "waybar-light.css",
]
HYPRLAND_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "hyprland-dark.conf",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "hyprland-light.conf",
]
ROFI_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "rofi-dark.rasi",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "rofi-light.rasi",
]
BTOP_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "btop-dreamcoder-dark.theme",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "btop-dreamcoder-light.theme",
]
DUNST_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "dunst-dreamcoder-dark.conf",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "dunst-dreamcoder-light.conf",
]
FZF_FILES = [
    ROOT / "DreamcoderThemes" / "dreamcoder" / "fzf-dreamcoder-dark.sh",
    ROOT / "DreamcoderThemes" / "dreamcoder" / "fzf-dreamcoder-light.sh",
]
HYPR_COLORS_LUA_GLOB = list((ROOT / "themes" / "dreamcoder").glob("hypr-colors-*.lua"))
HYPR_COLORS_CONF_GLOB = list((ROOT / "themes" / "dreamcoder").glob("hypr-colors-*.conf"))
TOKEN_PARITY_KEYS = [
    "bg",
    "bg_soft",
    "surface0",
    "surface1",
    "surface2",
    "surface3",
    "text",
    "text_heading",
    "muted",
    "subtle",
    "comment",
    "border",
    "border_ui",
    "border_hi",
    "focus",
    "accent",
    "accent_2",
    "diagnostic",
    "sage",
    "success",
    "info",
    "error",
    "warning",
    "lavender",
    "mauve",
    "on_surface",
    "on_accent",
    "on_error",
    "on_focus",
    "link",
    "link_hover",
    "selection_bg",
    "selection_fg",
    "disabled",
    "hover",
    "pressed",
]
ON_PAIRS = [
    ("on_accent", "accent"),
    ("on_error", "error"),
    ("on_focus", "focus"),
    ("selection_fg", "selection_bg"),
]
TEXT_KEYS = ["text", "textMuted", "primary", "info", "success", "error", "warning"]
UI_KEYS = ["border", "borderActive", "borderFocus"]
QUIET_UI_KEYS = ["border"]
BACKGROUND_KEYS = [
    "backgroundPanel",
    "backgroundElement",
    "backgroundHover",
    "backgroundCode",
    "backgroundLine",
    "diffAddedBg",
    "diffRemovedBg",
    "diffHunkHeaderBg",
]
SELECTED_BACKGROUND_KEYS = ["backgroundSelected"]
SYNTAX_KEYS = [
    "syntaxKeyword",
    "syntaxFunction",
    "syntaxMethod",
    "syntaxVariable",
    "syntaxParameter",
    "syntaxProperty",
    "syntaxField",
    "syntaxString",
    "syntaxType",
    "syntaxEnum",
    "syntaxOperator",
    "syntaxComment",
    "syntaxTodo",
    "syntaxDeprecated",
]
TOKEN_TEXT_KEYS = [
    "text",
    "muted",
    "comment",
    "accent",
    "accent_2",
    "diagnostic",
    "sage",
    "error",
    "warning",
]
TOKEN_BODY_APCA_KEYS = ["text", "error", "warning"]
TOKEN_INFO_APCA_KEYS = ["diagnostic"]
TOKEN_ACCENT_APCA_KEYS = ["accent", "accent_2", "sage"]
TOKEN_QUIET_APCA_KEYS = ["muted", "comment", "subtle"]
TOKEN_UI_KEYS = ["border_ui", "focus"]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
# RGBA pattern: rgba(r, g, b, a) with r/g/b 0-255 and a 0.0-1.0
RGBA = re.compile(r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(0|1|0?\.?\d+)\s*\)$")


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lum(value):
    def channel(part):
        part /= 255
        return part / 12.92 if part <= 0.03928 else ((part + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(part) for part in rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"unable to load JSON from {path}: {error}") from error


def is_valid_rgba(value: str) -> bool:
    """Validate RGBA format and component ranges."""
    match = RGBA.match(value)
    if not match:
        return False
    try:
        r, g, b, a = (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            float(match.group(4)),
        )
    except (TypeError, ValueError):
        return False
    return all(0 <= v <= 255 for v in (r, g, b)) and 0.0 <= a <= 1.0


def check_rgba_tokens():
    """Validate all rgba and inactive_border fields in tokens.json."""
    tokens = _load_json(TOKEN_FILE)
    rgba_keys = ["panel_rgba", "module_rgba", "active_rgba", "inactive_border"]

    for mode, palette in tokens["modes"].items():
        for key in rgba_keys:
            if key not in palette:
                continue
            value = palette[key]
            require(
                is_valid_rgba(value),
                f"tokens:{mode}:{key} invalid RGBA format: {value}",
            )


def check_apca_require(mode, key, value, bg, threshold):
    """Fail CI when APCA body/heading pairs miss targets."""
    lc = abs(apca_lc(value, bg))
    require(
        lc >= threshold,
        f"tokens:{mode}:{key} APCA Lc {lc:.1f} < {threshold}",
    )


def check_token_parity(tokens):
    dark = tokens["modes"]["dark"]
    light = tokens["modes"]["light"]
    dark_keys = {
        key
        for key, value in dark.items()
        if key not in {"name", "details"} and isinstance(value, str)
    }
    light_keys = {
        key
        for key, value in light.items()
        if key not in {"name", "details"} and isinstance(value, str)
    }
    require(dark_keys == light_keys, f"dark/light token key mismatch: {dark_keys ^ light_keys}")
    for key in TOKEN_PARITY_KEYS:
        require(key in dark, f"tokens:dark missing parity key {key}")
        require(key in light, f"tokens:light missing parity key {key}")


def check_tokens():
    tokens = _load_json(TOKEN_FILE)
    guardrails = tokens["guardrails"]
    apca_body_light = guardrails.get("minimum_apca_body", 75)
    apca_body_dark = guardrails.get("minimum_apca_body_dark", 60)
    apca_quiet = guardrails.get("minimum_apca_quiet", 55)
    apca_ui_light = guardrails.get("minimum_apca_ui", 60)
    apca_ui_dark = guardrails.get("minimum_apca_ui_dark", 28)
    terminal_ansi_min = guardrails.get("minimum_terminal_ansi_contrast", 4.5)
    terminal_cursor_min = guardrails.get("minimum_terminal_cursor_contrast", 4.5)
    apca_heading_light = guardrails.get("minimum_apca_heading_light", 60)
    apca_heading_dark = guardrails.get("minimum_apca_heading_dark", 45)
    apca_on_accent = guardrails.get("minimum_apca_on_accent", 60)
    terminal_selection_min = guardrails.get("minimum_terminal_selection_contrast", 7.0)
    require(
        guardrails["canonical_opencode_theme"] == "dreamcoder",
        "tokens: canonical opencode theme must be dreamcoder",
    )
    check_token_parity(tokens)
    for mode, palette in tokens["modes"].items():
        bg = palette["bg"]
        require(HEX.match(bg), f"tokens:{mode}: invalid background")
        # Dark's surface policy reserves pure black for the canvas.
        # Light/dusk must still avoid harsh pure black/white backgrounds.
        if mode != "dark":
            require(bg.lower() not in {"#000000", "#ffffff"}, f"tokens:{mode}: harsh background")
        for key in TOKEN_TEXT_KEYS:
            require(key in palette, f"tokens:{mode}:{key}: missing token")
            value = palette[key]
            require(HEX.match(value), f"tokens:{mode}:{key}: invalid hex")
            require(contrast(bg, value) >= 4.5, f"tokens:{mode}:{key} contrast below 4.5")
        if palette.get("details") == "lighter":
            apca_body = apca_body_light
            apca_body_keys = TOKEN_BODY_APCA_KEYS
            apca_accent = apca_body_dark
            apca_accent_keys = TOKEN_ACCENT_APCA_KEYS
        else:
            apca_body = apca_body_dark
            apca_body_keys = TOKEN_BODY_APCA_KEYS
            apca_accent_keys = []
            apca_accent = apca_body_dark
        for key in apca_body_keys:
            value = palette[key]
            check_apca_require(mode, key, value, bg, apca_body)
        for key in TOKEN_INFO_APCA_KEYS:
            if key not in palette:
                continue
            info_target = 42 if palette.get("details") == "darker" else apca_body
            check_apca_require(mode, key, palette[key], bg, info_target)
        if "text_heading" in palette:
            heading_target = apca_heading_light if mode == "light" else apca_heading_dark
            check_apca_require(mode, "text_heading", palette["text_heading"], bg, heading_target)
        for key in apca_accent_keys:
            value = palette[key]
            check_apca_require(mode, key, value, bg, apca_accent)
        for key in TOKEN_QUIET_APCA_KEYS:
            if key not in palette:
                continue
            value = palette[key]
            check_apca_require(mode, key, value, bg, apca_quiet)
        require(contrast(bg, palette["text"]) >= 7, f"tokens:{mode}: main text below AAA")
        check_apca_require(mode, "text", palette["text"], bg, apca_body)
        for fg_key, bg_key in ON_PAIRS:
            require(
                fg_key in palette and bg_key in palette, f"tokens:{mode}: missing {fg_key}/{bg_key}"
            )
            pair_ratio = contrast(palette[fg_key], palette[bg_key])
            require(pair_ratio >= 4.5, f"tokens:{mode}:{fg_key}/{bg_key} {pair_ratio:.2f} < 4.5")
            if fg_key == "on_accent":
                check_apca_require(mode, fg_key, palette[fg_key], palette[bg_key], apca_on_accent)
        for index, color in enumerate(terminal_ansi(palette)):
            require(
                contrast(color, bg) >= terminal_ansi_min,
                f"tokens:{mode}: ANSI color{index} contrast {contrast(color, bg):.2f} < {terminal_ansi_min}",
            )
        sel_fg = palette["selection_fg"]
        sel_bg = palette["selection_bg"]
        require(
            contrast(palette["accent"], bg) >= terminal_cursor_min,
            f"tokens:{mode}: cursor contrast {contrast(palette['accent'], bg):.2f} < {terminal_cursor_min}",
        )
        require(
            contrast(sel_fg, sel_bg) >= terminal_selection_min,
            f"tokens:{mode}: selection pair contrast {contrast(sel_fg, sel_bg):.2f} < {terminal_selection_min}",
        )
        require(
            palette["border_ui"] != palette["border_hi"],
            f"tokens:{mode}: border_ui and border_hi must differ",
        )
        require(
            palette["comment"] != palette["subtle"],
            f"tokens:{mode}: comment and subtle must differ",
        )
        require(
            palette["focus"] != palette["diagnostic"],
            f"tokens:{mode}: focus and diagnostic must differ",
        )
        require(
            palette["accent"] != palette["accent_2"],
            f"tokens:{mode}: accent and accent_2 must differ",
        )
        apca_ui = apca_ui_light if mode == "light" else apca_ui_dark
        for key in TOKEN_UI_KEYS:
            require(key in palette, f"tokens:{mode}:{key}: missing UI token")
            value = palette[key]
            require(HEX.match(value), f"tokens:{mode}:{key}: invalid hex")
            require(contrast(bg, value) >= 3, f"tokens:{mode}:{key} contrast below 3.0")
            check_apca_require(mode, key, value, bg, apca_ui)


def check_dual_gate_candidates():
    """Validate the package dual gate on all three deterministic candidates:
    Light, Dark, and design-system Dusk. Any dual-gate error blocks."""
    tokens = load_tokens(TOKEN_FILE)
    # float() narrows the comprehension to dict[str, float] (mirrors
    # palette.load_guardrails), satisfying the dict-invariance typing.
    try:
        guardrails = {
            k: float(v) for k, v in tokens["guardrails"].items() if isinstance(v, int | float)
        }
    except (TypeError, ValueError) as error:
        raise SystemExit(f"invalid numeric guardrail: {error}") from error
    candidates = [
        ("light", tokens["modes"]["light"], "light"),
        ("dark", tokens["modes"]["dark"], "dark"),
        ("dusk", tokens["modes"]["dusk"], "dusk"),
    ]
    for label, palette, mode in candidates:
        errors = validate_palette(palette, guardrails, mode=mode)
        require(not errors, f"dual gate {label}:\n" + "\n".join(errors))


def check_coverage_declaration():
    """Fail when the sync 33-consumer coverage declaration is missing,
    duplicated, or not exactly the design matrix's 33 IDs."""
    from dreamcoder_theme.sync import COVERAGE

    ids = [row.consumer_id for row in COVERAGE]
    require(len(ids) == 33, f"coverage: expected 33 consumer IDs, got {len(ids)}")
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    require(not dupes, f"coverage: duplicate consumer IDs: {dupes}")


def check_antigravity_files():
    """Validate Antigravity's semantic button pair for every mode file."""
    if not any(file.exists() for file in ANTIGRAVITY_FILES):
        return
    tokens = load_tokens(TOKEN_FILE)
    palettes = {
        "Dreamcoder.json": tokens["modes"]["dark"],
        "Dreamcoder-Dark.json": tokens["modes"]["dark"],
        "Dreamcoder-Light.json": tokens["modes"]["light"],
    }
    for file in ANTIGRAVITY_FILES:
        colors = _load_json(file)["colors"]
        palette = palettes[file.name]
        background = colors["button.background"]
        foreground = colors["button.foreground"]
        require(
            background == palette["accent_2"],
            f"{file}: button.background must resolve accent_2",
        )
        require(
            foreground == palette["on_accent"],
            f"{file}: button.foreground must resolve on_accent",
        )
        ratio = contrast(background, foreground)
        require(ratio >= 4.5, f"{file}: button contrast {ratio:.2f} < 4.5")


def check_theme_file(file, mode=None):
    if not file.exists():
        return
    theme = _load_json(file)["theme"]
    bg = theme["background"]
    # Dark's surface policy reserves pure black for the canvas.
    # Light/dusk must still avoid harsh pure black/white backgrounds.
    if mode != "dark":
        require(
            bg not in {"#000000", "#ffffff"},
            f"{file}: background uses harsh pure black/white",
        )
        require(0.004 < lum(bg) < 0.94, f"{file}: background luminance is outside comfort band")
    for key in TEXT_KEYS + SYNTAX_KEYS:
        ratio = contrast(bg, theme[key])
        require(ratio >= 4.5, f"{file}: {key} contrast {ratio:.2f} < 4.5")
    for key in UI_KEYS:
        ratio = contrast(bg, theme[key])
        require(ratio >= 3, f"{file}: {key} UI contrast {ratio:.2f} < 3")
        if key in QUIET_UI_KEYS:
            require(ratio <= 7, f"{file}: {key} UI contrast {ratio:.2f} is too loud")
    for key in BACKGROUND_KEYS:
        ratio = contrast(bg, theme[key])
        require(ratio >= 1.05, f"{file}: {key} surface contrast {ratio:.2f} < 1.05")
        require(ratio <= 2.4, f"{file}: {key} surface contrast {ratio:.2f} > 2.4")
    for key in SELECTED_BACKGROUND_KEYS:
        ratio = contrast(bg, theme[key])
        require(ratio >= 1.05, f"{file}: {key} surface contrast {ratio:.2f} < 1.05")
        require(ratio <= 2.4, f"{file}: {key} surface contrast {ratio:.2f} > 2.4")
    require(
        contrast(theme["terminalCyan"], theme["background"])
        >= contrast(theme["terminalBlue"], theme["background"]),
        f"{file}: terminal cyan should be at least as legible as terminal blue",
    )
    require(contrast(bg, theme["text"]) >= 7, f"{file}: main text contrast below AAA")


def check_codex_cli_theme(file):
    if not file.exists():
        return
    data = plistlib.loads(file.read_bytes())
    settings = data["settings"][0]["settings"]
    bg = settings["background"]
    fg = settings["foreground"]
    require(HEX.match(bg), f"{file}: invalid background")
    require(HEX.match(fg), f"{file}: invalid foreground")
    require(contrast(bg, fg) >= 7, f"{file}: foreground contrast below AAA")
    require(contrast(bg, settings["selection"]) >= 1.05, f"{file}: selection too faint")
    require(contrast(bg, settings["selection"]) <= 2.4, f"{file}: selection too loud")
    if lum(bg) > 0.5:
        require(
            contrast(bg, settings["lineHighlight"]) >= 1.15,
            f"{file}: light line highlight too faint",
        )
        require(contrast(bg, settings["gutter"]) >= 1.45, f"{file}: light gutter too faint")


def _load_generator():
    path = ROOT / "scripts" / "generate-palette-tokens.py"
    spec = importlib.util.spec_from_file_location("dreamcoder_palette_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _health_findings():
    """Return deterministic Phase 2 errors before running legacy guardrails."""
    findings = []
    tokens = load_tokens(TOKEN_FILE)
    contract = load_contract(DESIGN_SYSTEM_CONTRACT_FILE)
    for document, schema_path in (
        (tokens, ROOT / "DreamcoderThemes/dreamcoder/tokens.schema.json"),
        (contract, ROOT / "DreamcoderThemes/dreamcoder/design-system.schema.json"),
    ):
        try:
            jsonschema.Draft202012Validator(json.loads(schema_path.read_text())).validate(document)
        except (json.JSONDecodeError, jsonschema.ValidationError) as error:
            findings.append(f"SCHEMA_INVALID: {schema_path.relative_to(ROOT)}: {error}")
    drift = _load_generator().check_generated(
        TOKEN_FILE, ROOT / "src/dreamcoder_theme/palette_tokens.py"
    )
    if drift:
        findings.append(drift)
    findings.extend(
        f"design-system:{finding.code}: {finding.message}"
        for finding in evaluate_contract(contract, tokens)
        if finding.severity == "error"
    )
    artifact = next(
        (item for item in contract.get("artifacts", []) if item.get("id") == "opencode-default"),
        None,
    )
    if artifact is None:
        findings.append("DECLARED_ARTIFACT_MISSING: opencode-default")
        return sorted(findings)
    artifact_path = artifact.get("path")
    if not isinstance(artifact_path, str) or not artifact_path:
        findings.append("MALFORMED_ARTIFACT: opencode-default missing path")
        return sorted(findings)
    theme_path = ROOT / artifact_path
    names = (
        sorted(path.name for path in OPENCODE_THEME_DIR.glob("*.json"))
        if OPENCODE_THEME_DIR.exists()
        else []
    )
    if names != ["dreamcoder.json"]:
        findings.append(
            f"UNOWNED_ARTIFACT: .opencode/themes expected ['dreamcoder.json'], got {names}"
        )
    if not theme_path.exists():
        findings.append("MALFORMED_ARTIFACT: missing {}".format(artifact["path"]))
    else:
        try:
            actual = theme_path.read_text(encoding="utf-8")
            json.loads(actual)
            # The design contract declares the opencode renderer for
            # dark/light/dusk; accept an artifact that exactly matches the
            # generator output for any declared mode (deterministic, not
            # coupled to the runner's live theme mode).
            expected_by_mode = {
                mode: opencode_content(tokens["modes"][mode], transparent_background=True)
                for mode in ("dark", "light", "dusk")
                if mode in tokens["modes"]
            }
            if actual not in set(expected_by_mode.values()):
                findings.append(
                    "STALE_ARTIFACT: .opencode/themes/dreamcoder.json "
                    "regeneration command=PYTHONPATH=src python -m dreamcoder_theme.sync"
                )
        except (json.JSONDecodeError, KeyError) as error:
            findings.append("MALFORMED_ARTIFACT: {}: {}".format(artifact["path"], error))
    return sorted(findings)


def check_opencode_repo():
    """Validate the declared .opencode/themes contract, not application configuration."""
    findings = _health_findings()
    require(not findings, "\n".join(findings))


def check_design_system_contract():
    """Fail health verification when the declared three-mode contract has findings."""
    findings = evaluate_contract(
        load_contract(DESIGN_SYSTEM_CONTRACT_FILE),
        load_tokens(TOKEN_FILE),
    )
    require(
        not findings,
        "\n".join(f"design-system:{finding.code}: {finding.message}" for finding in findings),
    )


def check_kitty_colors(file):
    """Validate Kitty colors file has valid hex colors."""
    if not file.exists():
        return
    content = file.read_text()
    # Check for required color definitions
    for color_key in ["background", "foreground"]:
        if re.search(rf"^{color_key}\s+#[0-9a-fA-F]{{6}}", content, re.M):
            continue
        require(False, f"{file}: missing {color_key} definition")


def check_starship_config(file):
    """Validate Starship config has valid hex for key elements."""
    if not file.exists():
        return
    content = file.read_text()
    # Check that at least some style blocks exist with valid hex
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 4, f"{file}: missing sufficient hex color definitions")


def check_ghostty_theme(file):
    """Validate Ghostty theme has valid hex background/foreground."""
    if not file.exists():
        return
    content = file.read_text()
    for key in ["background", "foreground"]:
        match = re.search(rf"^{key}\s*=\s*#[0-9a-fA-F]{{6}}", content, re.M)
        require(bool(match), f"{file}: missing or invalid {key}")


def check_waybar_css(file):
    """Validate Waybar CSS has valid colors."""
    if not file.exists():
        return
    content = file.read_text()
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 2, f"{file}: missing sufficient hex color definitions")


def check_hypr_config(file):
    """Validate Hyprland config has valid colors for borders/backgrounds."""
    if not file.exists():
        return
    content = file.read_text()
    # Hyprland uses rgba(RRGGBBAA) compact format and col.*= hex formats
    has_rgba = bool(re.search(r"rgba\([0-9a-fA-F]{8}\)", content))
    has_hex = bool(re.search(r"col\.[a-z_]+\s*=\s*#[0-9a-fA-F]{6}", content))
    require(has_rgba or has_hex, f"{file}: missing valid color definitions")


def check_rofi_theme(file):
    """Validate Rofi CSS has valid colors."""
    if not file.exists():
        return
    content = file.read_text()
    # Rofi .rasi files use hex colors in * { color: #RRGGBB; } blocks
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 4, f"{file}: missing sufficient hex color definitions")


def check_btop_theme(file):
    """Validate Btop theme has valid colors."""
    if not file.exists():
        return
    content = file.read_text()
    # Btop themes use color definitions like: color0=XXXXXX
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 4, f"{file}: missing sufficient hex color definitions")


def check_dunst_theme(file):
    """Validate Dunst config has valid colors."""
    if not file.exists():
        return
    content = file.read_text()
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 1, f"{file}: missing hex color definitions")


def check_fzf_theme(file):
    """Validate Fzf shell snippet has valid exports."""
    if not file.exists():
        return
    content = file.read_text()
    hex_matches = re.findall(r"#[0-9a-fA-F]{6}", content)
    require(len(hex_matches) >= 1, f"{file}: missing hex color definitions")


def check_hypr_colors_file(file):
    """Validate a hypr-colors lua/conf file has valid color definitions."""
    if not file.exists():
        return
    content = file.read_text()
    has_rgba = bool(re.search(r"rgba\([0-9a-fA-F]{8}\)", content))
    require(has_rgba, f"{file}: missing valid rgba color definitions")


check_rgba_tokens()
check_tokens()
for file, mode in (
    (FILES[0], "dark"),
    (FILES[1], "light"),
    (FILES[2], "dark"),
):
    check_theme_file(file, mode=mode)
for file in CODEX_CLI_FILES:
    check_codex_cli_theme(file)
check_opencode_repo()
check_design_system_contract()
check_dual_gate_candidates()
check_coverage_declaration()
check_antigravity_files()
for file in KITTY_FILES:
    check_kitty_colors(file)
for file in STARSHIP_FILES:
    check_starship_config(file)
for file in GHOSTTY_FILES:
    check_ghostty_theme(file)
for file in WAYBAR_FILES:
    check_waybar_css(file)
for file in HYPRLAND_FILES:
    check_hypr_config(file)
for file in ROFI_FILES:
    check_rofi_theme(file)
for file in BTOP_FILES:
    check_btop_theme(file)
for file in DUNST_FILES:
    check_dunst_theme(file)
for file in FZF_FILES:
    check_fzf_theme(file)
for file in HYPR_COLORS_LUA_GLOB:
    check_hypr_colors_file(file)
for file in HYPR_COLORS_CONF_GLOB:
    check_hypr_colors_file(file)
print("✓ Dreamcoder theme health guardrails passed")
