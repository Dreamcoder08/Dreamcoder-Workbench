#!/usr/bin/env python3
"""Check wallpapers against the Dreamcoder wallpaper <-> UI contract.

The limits come from components.wallpaper.<mode> in tokens.json. Each image is
read through ImageMagick (`magick`), downsampled to 480x270 and measured in
OKLab. Prints `OK FILE`, or one `FILE: CODE: message` line per violated rule.
Reads files only; writes nothing.

Exit codes: 0 every file passes, 1 at least one finding, 2 usage or setup error.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dreamcoder_theme.palette_tokens import VARIANTS  # noqa: E402
from dreamcoder_theme.wallpaper_contract import (  # noqa: E402
    Finding,
    Pixel,
    evaluate,
    load_contract,
)

DEFAULT_TOKENS = ROOT / "DreamcoderThemes" / "dreamcoder" / "tokens.json"
GRID_WIDTH = 480
GRID_HEIGHT = 270


class UnreadableImageError(Exception):
    """ImageMagick could not read the file as an image."""


def imagemagick() -> tuple[list[str], list[str]] | None:
    """(convert, identify) command prefixes: IM7 `magick`, else IM6 `convert` + `identify`."""
    if shutil.which("magick"):
        return ["magick"], ["magick", "identify"]
    if shutil.which("convert") and shutil.which("identify"):
        return ["convert"], ["identify"]
    return None


def _imagemagick_output(command: list[str]) -> bytes:
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        raise UnreadableImageError(
            detail[0] if detail else f"{command[0]} exited {result.returncode}"
        )
    return result.stdout


def read_image(path: str) -> tuple[tuple[int, int], list[Pixel]]:
    """(width, height) of the file and its 480x270 sRGB downsample."""
    tools = imagemagick()
    if tools is None:
        raise UnreadableImageError("ImageMagick is not installed")
    convert, identify = tools
    absolute = os.path.abspath(path)  # an absolute path is never read as `format:` or `@list`
    size = _imagemagick_output([*identify, "-format", "%w %h", absolute]).decode().split()
    raw = _imagemagick_output(
        [*convert, absolute, "-resize", f"{GRID_WIDTH}x{GRID_HEIGHT}!", "-depth", "8", "rgb:-"]
    )
    if len(size) < 2 or len(raw) != GRID_WIDTH * GRID_HEIGHT * 3:
        raise UnreadableImageError("unexpected image data")
    return (int(size[0]), int(size[1])), list(zip(raw[0::3], raw[1::3], raw[2::3], strict=True))


def check_file(path: str, mode: str, contract: dict[str, Any]) -> list[Finding]:
    try:
        size, pixels = read_image(path)
    except UnreadableImageError as error:
        return [Finding("WALLPAPER_UNREADABLE", str(error))]
    return evaluate(
        pixels,
        grid_width=GRID_WIDTH,
        source_size=size,
        mode=mode,
        contract=contract,
        palette=VARIANTS[mode],
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0] if __doc__ else None,
        epilog=__doc__.split("\n\n", 1)[1] if __doc__ else None,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=("light", "dark"), required=True)
    parser.add_argument(
        "--tokens",
        type=Path,
        default=DEFAULT_TOKENS,
        help="tokens.json holding components.wallpaper (default: the repository file)",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="wallpaper image to check")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if imagemagick() is None:
        print(
            "check-wallpaper: ImageMagick is required (`magick`, or `convert` and `identify`)",
            file=sys.stderr,
        )
        return 2
    try:
        contract = load_contract(json.loads(arguments.tokens.read_text("utf-8")), arguments.mode)
    except (OSError, ValueError, KeyError) as error:
        print(
            f"check-wallpaper: no wallpaper contract in {arguments.tokens}: {error}",
            file=sys.stderr,
        )
        return 2
    failed = False
    for path in arguments.files:
        findings = check_file(path, arguments.mode, contract)
        if not findings:
            print(f"OK {path}")
        for finding in findings:
            print(f"{path}: {finding.code}: {finding.message}")
        failed = failed or bool(findings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
