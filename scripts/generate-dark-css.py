#!/usr/bin/env python3
"""Generate the Dreamcoder Dark CSS variables from canonical Dreamcoder tokens."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TOKENS_FILE = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"
OUTPUT = ROOT / "DreamcoderThemes" / "dreamcoder" / "dreamcoder-dark.css"


def load_tokens(path: Path = TOKENS_FILE) -> dict[str, Any]:
    """Load canonical JSON tokens without mutating the source."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load canonical tokens from {path}: {exc}") from exc


_HEX_TOKEN = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_DECIMAL_ZEROS = re.compile(r"(\.\d*?)0+")


def _canonical(value: object) -> str:
    """Canonical serialization: lowercase hex colors, trimmed decimal zeros."""
    text = str(value)
    text = _HEX_TOKEN.sub(lambda match: match.group(0).lower(), text)
    previous = None
    while previous != text:
        previous = text
        text = _DECIMAL_ZEROS.sub(r"\1", text)
    return text


def render_css(tokens: dict[str, Any]) -> str:
    """Render deterministic CSS from the canonical dark mode and surface policy."""
    dark = tokens["modes"]["dark"]
    aliases = dark["aliases"]
    effects = dark["effects"]
    typography = dark["typography"]
    surface_policy = dark["surface_policy"]
    scroll_surface = surface_policy["scroll_surface"]

    variables = (
        ("bg", dark["bg"]),
        ("surface-0", dark["surface0"]),
        ("surface-1", dark["surface1"]),
        ("surface-2", dark["surface2"]),
        ("surface-3", dark["surface3"]),
        ("surface-scroll", dark[scroll_surface]),
        ("hover", dark["hover"]),
        ("border-subtle", aliases["border_subtle"]),
        ("border-medium", aliases["border_medium"]),
        ("border-focus", dark["focus"]),
        ("border-runtime", dark["border"]),
        ("text-primary", dark["text"]),
        ("text-secondary", dark["muted"]),
        ("text-muted", aliases["text_muted"]),
        ("accent-brand", aliases["brand"]),
        ("accent-runtime", dark["accent"]),
        ("accent-secondary", dark["accent_2"]),
        ("focus", dark["focus"]),
        ("success", dark["success"]),
        ("warning", dark["warning"]),
        ("error", aliases["error_requested"]),
        ("error-runtime", dark["error"]),
        ("info", dark["info"]),
        ("syntax-comment", dark["comment"]),
        ("syntax-keyword", dark["mauve"]),
        ("syntax-function", dark["accent"]),
        ("syntax-string", dark["success"]),
        ("syntax-number", dark["warning"]),
        ("syntax-type", dark["lavender"]),
        ("syntax-operator", dark["diagnostic"]),
        ("glow-brand", effects["glow_brand"]),
        ("glow-focus", effects["glow_focus"]),
        ("glow-error", effects["glow_error"]),
        ("font-weight-body", typography["body_weight"]),
        ("font-weight-emphasis", typography["emphasis_weight"]),
        ("font-weight-heading", typography["heading_weight"]),
        ("letter-spacing", typography["letter_spacing"]),
        ("letter-spacing-uppercase", typography["uppercase_letter_spacing"]),
    )

    lines = [
        "/* AUTO-GENERATED from tokens.json. Run: python scripts/generate-dark-css.py */",
        "/* Scrollable workspaces and editors use --dc-surface-scroll to avoid pure-black smear. */",
        "/* Typography: use body 400, emphasis 500, headings 600; reserve uppercase tracking for labels. */",
        f"{surface_policy['selector']} {{",
    ]
    lines.extend(f"  --dc-{name}: {_canonical(value)};" for name, value in variables)
    lines.extend(("}", ""))
    return "\n".join(lines)


def _display_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def drift_message(source: Path, output: Path) -> str:
    return (
        "GENERATED_DRIFT: canonical source="
        f"{_display_path(source)} generated path={_display_path(output)} "
        "regeneration command=python scripts/generate-dark-css.py"
    )


def check_generated(tokens_path: Path = TOKENS_FILE, output_path: Path = OUTPUT) -> str | None:
    """Return a drift diagnostic without writing files."""
    expected = render_css(load_tokens(tokens_path))
    actual = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    return None if actual == expected else drift_message(tokens_path, output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated CSS is stale")
    args = parser.parse_args(argv)

    if args.check:
        drift = check_generated()
        if drift:
            print(drift, file=sys.stderr)
            return 1
        print(f"✓ Generated CSS synchronized: {OUTPUT.relative_to(ROOT)}")
        return 0

    OUTPUT.write_text(render_css(load_tokens()), encoding="utf-8")
    print(f"✓ Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
