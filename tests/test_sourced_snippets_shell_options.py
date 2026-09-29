"""Snippets meant to be ``source``d must never change the caller's shell options.

``.zshrc`` sources the LS_COLORS, fzf and bat snippets directly; a
``set -euo pipefail`` inside them turned errexit/nounset on in the interactive
shell, so the first failing command closed the terminal.
"""

from __future__ import annotations

import re

import pytest

from dreamcoder_theme.palette import load_variants
from dreamcoder_theme.palette_tokens import VARIANTS as DEFAULT_VARIANTS
from dreamcoder_theme.renderers_extra_bat_delta import bat_content
from dreamcoder_theme.renderers_extra_shell import fzf_content, ls_colors_content
from dreamcoder_theme.settings import theme_paths

SHELL_OPTION = re.compile(r"^\s*set\s+[-+][a-z]", re.MULTILINE)


@pytest.mark.parametrize("render", [ls_colors_content, fzf_content, bat_content])
@pytest.mark.parametrize("mode", ["light", "dark"])
def test_sourced_snippet_sets_no_shell_options(render, mode):
    palette = load_variants(DEFAULT_VARIANTS, theme_paths().tokens_file)[mode]
    assert not SHELL_OPTION.search(render(palette))
