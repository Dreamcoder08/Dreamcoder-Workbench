"""Claude Code custom theme (``~/.claude/themes/<slug>.json``).

Claude Code's built-in Light paints saturated green/pink diff bands. A custom
theme keeps its matching base for every other token and overrides only the
diff backgrounds with palette tints, the same approach as the OpenCode diffs:
the line band reads clearly, the word highlight is stronger, and body text
keeps >= 7:1 on all of them.
"""

from __future__ import annotations

import json

from ._math import mix
from .palette import detect_mode

# (line band, word highlight, dimmed band after a rejected edit)
_TINTS = {"light": (0.12, 0.26, 0.05), "dark": (0.20, 0.36, 0.10)}


def claude_code_theme_content(palette: dict[str, str]) -> str:
    """Render a Claude Code theme whose diff bands follow the palette."""
    mode = detect_mode(palette)
    line, word, dimmed = _TINTS[mode]
    overrides: dict[str, str] = {}
    for kind, token in (("Added", "success"), ("Removed", "error")):
        overrides[f"diff{kind}"] = mix(palette["bg"], palette[token], line)
        overrides[f"diff{kind}Dimmed"] = mix(palette["bg"], palette[token], dimmed)
        overrides[f"diff{kind}Word"] = mix(palette["bg"], palette[token], word)
    theme = {"name": "Dreamcoder", "base": mode, "overrides": overrides}
    return json.dumps(theme, indent=2) + "\n"
