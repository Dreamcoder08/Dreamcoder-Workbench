#!/usr/bin/env python3
"""Generate palette_tokens.py from DreamcoderThemes/dreamcoder/tokens.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS_FILE = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"
OUTPUT = ROOT / "src" / "dreamcoder_theme" / "palette_tokens.py"
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dreamcoder_theme.color_space import (  # noqa: E402
    hex_to_oklch,
    oklch_to_hex,
)
from dreamcoder_theme.color_space import (  # noqa: E402
    hex_to_unit_rgb as hex_to_rgb,
)
from dreamcoder_theme.color_space import (  # noqa: E402
    unit_rgb_to_hex as rgb_to_hex,
)

ANSI_KEY_NAMES = [
    "surface0",
    "error",
    "success",
    "warning",
    "info",
    "mauve",
    "lavender",
    "muted",
    "subtle",
    "error_bright",
    "success_bright",
    "warning_bright",
    "info_bright",
    "mauve_bright",
    "focus_bright",
    "text",
]


def mix_hex(left: str, right: str, amount: float) -> str:
    a = hex_to_rgb(left)
    b = hex_to_rgb(right)
    return rgb_to_hex(
        (
            a[0] + (b[0] - a[0]) * amount,
            a[1] + (b[1] - a[1]) * amount,
            a[2] + (b[2] - a[2]) * amount,
        )
    )


def ramp_step(base: str, target_l_delta: float) -> str:
    lightness, chroma, hue = hex_to_oklch(base)
    return oklch_to_hex(max(0, min(1, lightness + target_l_delta)), chroma, hue)


def rgba_from_hex(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {alpha:.2f})"


def enrich_mode(mode: dict[str, object]) -> dict[str, str]:
    """Fill derived semantic tokens while excluding non-palette mode metadata."""
    c = {key: value for key, value in mode.items() if isinstance(value, str)}
    is_dark = c.get("details") == "darker"
    bg = c["bg"]
    text = c["text"]

    c.setdefault("success", c["sage"])
    c.setdefault("info", c["diagnostic"])
    c.setdefault("text_heading", ramp_step(text, 0.04 if is_dark else -0.03))
    c.setdefault("surface3", ramp_step(c["surface2"], -0.04 if is_dark else -0.05))

    c.setdefault("selection_bg", c.get("surface1", c["bg"]))
    c.setdefault("selection_fg", text)
    c["selection"] = c["selection_bg"]

    on_light = c.get("surface0", "#ffffff")
    on_dark = c.get("prompt_text", bg)
    c.setdefault("on_surface", text)
    c.setdefault("on_accent", on_dark if is_dark else on_light)
    c.setdefault("on_error", c["on_accent"])
    c.setdefault("on_focus", c["on_accent"])

    c.setdefault("link", c["accent"])
    c.setdefault("link_hover", c["accent_2"])
    c.setdefault("disabled", mix_hex(c["muted"], bg, 0.35))
    c.setdefault("hover", c["surface1"])
    c.setdefault("pressed", c["surface2"])
    c.setdefault("overlay", rgba_from_hex(bg, 0.52 if is_dark else 0.40))
    c.setdefault("scrim", "rgba(0, 0, 0, 0.58)" if is_dark else "rgba(26, 18, 12, 0.42)")

    if "panel_rgba" not in c:
        c["panel_rgba"] = rgba_from_hex(bg, 0.78 if is_dark else 0.96)
    if "module_rgba" not in c:
        fg = mix_hex(text, bg, 0.08 if is_dark else 0.0)
        c["module_rgba"] = rgba_from_hex(fg, 0.08 if is_dark else 0.80)
    if "active_rgba" not in c:
        c["active_rgba"] = rgba_from_hex(c["accent"], 0.24 if is_dark else 0.34)
    if "inactive_border" not in c:
        c["inactive_border"] = rgba_from_hex(c["border"], 0.50 if is_dark else 0.93)

    return c


def _add_trailing_commas(text: str) -> str:
    """Convert json.dumps output to ruff-format multiline style.

    json.dumps never emits trailing commas; the repository formatter
    (ruff-format) keeps trailing commas on multiline collections, so a
    regenerated file would otherwise drift from the committed style and
    fail the generated-artifact check. Add a trailing comma to every value
    line (and nested closing brace/bracket) that is followed by a closing
    brace or bracket.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for index, line in enumerate(lines):
        stripped = line.rstrip()
        nxt = lines[index + 1].lstrip() if index + 1 < len(lines) else ""
        ends_value = bool(stripped) and not stripped.endswith(("{", "[", ","))
        if ends_value and (nxt.startswith("}") or nxt.startswith("]")):
            out.append(stripped + ",\n")
        else:
            out.append(line)
    return "".join(out)


def render_palette_tokens(variants: dict[str, dict[str, str]]) -> str:
    lines = [
        '"""Static palette token data for Dreamcoder themes.',
        "",
        "AUTO-GENERATED from DreamcoderThemes/dreamcoder/tokens.json — do not edit by hand.",
        "Run: ./scripts/generate-palette-tokens.py",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "VARIANTS = " + _add_trailing_commas(json.dumps(variants, indent=4)) + "",
        "",
        "ANSI_KEY_NAMES = " + _add_trailing_commas(json.dumps(ANSI_KEY_NAMES, indent=4)) + "",
        "",
    ]
    return "\n".join(lines)


def load_tokens(path: Path = TOKENS_FILE) -> dict[str, object]:
    """Load canonical tokens without modifying their source file."""
    try:
        data: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load canonical tokens from {path}: {exc}") from exc
    return data


def enrich_tokens(tokens: dict[str, object]) -> dict[str, object]:
    """Return a generated view with derived tokens, leaving canonical input untouched."""
    result = dict(tokens)
    modes = tokens.get("modes", {})
    if not isinstance(modes, dict):
        raise ValueError("tokens.modes must be an object")
    result["modes"] = {
        name: enrich_mode(palette) for name, palette in modes.items() if isinstance(palette, dict)
    }
    guardrails_raw = tokens.get("guardrails", {})
    if not isinstance(guardrails_raw, dict):
        raise ValueError("tokens.guardrails must be an object")
    guardrails = dict(guardrails_raw)
    guardrails.setdefault("minimum_apca_on_accent", 60)
    guardrails.setdefault("minimum_apca_heading_light", 60)
    guardrails.setdefault("minimum_apca_heading_dark", 45)
    result["guardrails"] = guardrails
    return result


def render_from_tokens(tokens: dict[str, object]) -> str:
    """Render deterministic static tokens for the two declared modes."""
    enriched = enrich_tokens(tokens)
    modes = enriched["modes"]
    if not isinstance(modes, dict):
        raise ValueError("generated modes must be an object")
    missing = [name for name in ("dark", "light") if name not in modes]
    if missing:
        raise ValueError(f"missing required modes: {', '.join(missing)}")
    return render_palette_tokens({name: modes[name] for name in ("dark", "light")})


def _display_path(path: Path) -> Path:
    """Prefer repository-relative diagnostics while supporting isolated test paths."""
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def generated_drift_message(source: Path, output: Path) -> str:
    return (
        "GENERATED_DRIFT: canonical source="
        f"{_display_path(source)} generated path={_display_path(output)} "
        "regeneration command=python scripts/generate-palette-tokens.py"
    )


def check_generated(tokens_path: Path = TOKENS_FILE, output_path: Path = OUTPUT) -> str | None:
    """Return an actionable drift diagnostic or None; never write files."""
    expected = render_from_tokens(load_tokens(tokens_path))
    actual = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    return None if actual == expected else generated_drift_message(tokens_path, output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated output is stale")
    args = parser.parse_args(argv)
    tokens = load_tokens()
    if args.check:
        drift = check_generated()
        if drift:
            print(drift, file=sys.stderr)
            return 1
        print(f"✓ Generated tokens synchronized: {OUTPUT.relative_to(ROOT)}")
        return 0
    OUTPUT.write_text(render_from_tokens(tokens), encoding="utf-8")
    print(f"✓ Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
