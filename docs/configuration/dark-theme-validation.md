# Validate Dreamcoder Dark states

Use this reference to distinguish generated-color checks from actual application rendering. Passing contrast checks is not a visual approval or a claim of superiority over other themes. Palette ownership and regeneration are documented in the [theme system](theme-system.md).

## Run the read-only checks

From the repository root:

```bash
python scripts/verify-theme-health.py
python -m pytest tests/test_dark_cross_app_states.py -q
```

The [cross-application audit](../../tests/test_dark_cross_app_states.py) checks 62 resolved text/background pairs: Kitty/Ghostty, Pi, tmux, Starship and Dunst. It checks Pi variable references, quiet-text APCA and all 18 Starship text styles. A mutation check verifies that unreadable 1:1 text fails. These commands do not deploy themes or change the active mode.

Dark Starship supplies `diag` as a compatibility alias for `diagnostic`, used by Python, Go, Docker and the AI-session label. This does not change the diagnostic color. Light and the internal transition mode retain their previous output; the alias correction does not apply to them.

## Capture representative states

Keep the application version, font, font size, terminal opacity, wallpaper and display scaling constant. Record those settings with each capture. Prefer isolated demonstration sessions rather than modifying an active project or exposing sensitive paths.

| Application | Capture | Check visually |
| --- | --- | --- |
| Kitty/Ghostty | Main text, selected text, cursor; active/inactive tabs where supported | Selection remains readable; active state and keyboard focus are distinguishable. |
| Pi | Normal text, thinking text, user/custom message, pending/success/error tool cards | Secondary text remains legible; diagnostic meaning is not conveyed by color alone. |
| OpenCode | Syntax-highlighted code, inline code, added/removed lines and line numbers | Actual syntax remains readable over diff fills; body and gutter agree. |
| tmux | Active/inactive windows, a message and copy mode | Copy selection is clear; inactive windows do not look disabled. |
| Starship | Directory/git context and an applicable Python, Go or Docker segment | Runtime segments resolve their color and do not fall back unexpectedly. |
| Desktop | Rofi selected/normal entries, Waybar active/inactive states, notification urgency levels | Evaluate the composed appearance, not an opaque substitute for a transparent fill. |

Use the same short content for code and diff captures, including comments, strings, numbers and punctuation:

```python
# A comment should remain secondary but readable.
name = "Dreamcoder"
count = 42
print(f"{name}: {count}")
```

For a diff, show the same line once as added and once as removed. Include the input area and its focus indicator in the capture. A shell-output-only screenshot does not establish syntax or diff readability.

## Evidence boundaries

- Rofi and Waybar emit alpha backgrounds. Their final colors depend on the compositor backdrop; this audit does not guess a wallpaper or flatten them onto black.
- Herdr profile fields are checked against supported schemas, but those fields alone do not identify which component paints a screenshot's sidebar.
- Focus borders are not body text. Do not apply a 4.5:1 text threshold to decorations and claim a non-text accessibility result.
- The audit assumes matching canonical terminal colors when an application inherits terminal foreground/background. It does not certify arbitrary terminal themes or transparency.
- Generated values do not prove application support, live reload, font rendering, comfort over long sessions or complete accessibility compliance. Those require runtime evidence and user evaluation.
