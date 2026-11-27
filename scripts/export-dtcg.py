#!/usr/bin/env python3
"""Write the Dreamcoder tokens as a DTCG 2025.10 document.

Reads `DreamcoderThemes/dreamcoder/tokens.json` (the single source) and writes
`docs/generated/dreamcoder.tokens.json` unless `--output` says otherwise. The
output is deterministic and generated: never edit it by hand.

Exit codes: 0 written, 2 unreadable or inconsistent tokens.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme.dtcg_export import ExportError, render_dtcg  # noqa: E402

TOKENS = ROOT / "DreamcoderThemes/dreamcoder/tokens.json"
DEFAULT_OUTPUT = ROOT / "docs/generated/dreamcoder.tokens.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tokens", type=Path, default=TOKENS, help="source tokens.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="file to write")
    args = parser.parse_args(argv)
    try:
        text = render_dtcg(json.loads(args.tokens.read_text(encoding="utf-8")))
    except (OSError, ValueError, ExportError) as error:
        print(f"export-dtcg: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"export-dtcg: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
