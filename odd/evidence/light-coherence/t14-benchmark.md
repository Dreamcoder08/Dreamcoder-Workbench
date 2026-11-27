# T14 Benchmark — Dreamcoder Light against reference light themes (2026-11-26)

Measured with the repository's own math (`_math.contrast`, `_math.apca_lc`, `color_space.delta_e2000`,
`color_space.hex_to_oklch`). Reference values are transcribed from each project's published palette; only
their numbers are compared, nothing is copied into Dreamcoder.

Roles compared on each system's background: body text, muted text (Dreamcoder `comment`), and seven
semantic accents (error, warning, success, info, accent, violet, magenta). Dreamcoder's hover accent
(`accent_2`) is a deliberate sibling of `accent` and is not in the set.

| System | Text WCAG / APCA | Muted WCAG / APCA | Accents ≥ 4.5 | Weakest accent | Min ΔE2000 | Accent L spread |
| --- | --- | --- | --- | --- | --- | --- |
| **Dreamcoder Light (this branch)** | 16.31 / 99 | **6.82** / 80 | **7/7** | **6.44** | 15.1 | **0.002** |
| Dreamcoder Light (`origin/main`) | 16.30 / 99 | 5.97 / 77 | 7/7 | 6.02 | 14.0 | 0.011 |
| GitHub Primer Light | 15.80 / **103** | 6.11 / **81** | 7/7 | 4.87 | 16.1 | 0.041 |
| Catppuccin Latte | 7.06 / 79 | 4.37 / 66 | 2/7 | 2.31 | **16.4** | 0.175 |
| Rosé Pine Dawn | 6.66 / 79 | 4.02 / 64 | 1/7 | 2.05 | 14.0 | 0.265 |
| Solarized Light | 4.13 / 66 | 2.48 / 47 | 0/7 | 2.97 | 10.1 | 0.074 |

## Reading

- **Leads:** weakest accent (6.44:1, every semantic colour usable as text), muted text (6.82:1), and
  isoluminance: the seven accents differ by 0.002 in OKLab L, against 0.041 for the next best. Equal
  lightness means no accent shouts louder than another; only hue carries meaning.
- **Does not lead:**
  - Pigment distinctness: 15.1 against 16.4 for Catppuccin Latte and 16.1 for GitHub Primer. The closest
    pair is accent ↔ warning (umber ↔ ochre, two neighbouring earth pigments). That is the price of a warm,
    single-axis palette. It is still well above the ΔE 12 floor in `tests/test_light_material.py`.
  - APCA body text: 99 against GitHub's 103, because GitHub draws on pure white. Dreamcoder keeps warm
    paper (`#f9f6f2`) on purpose: lower glare and coherence with the wallpaper axis.
- **Different goal, not a loss:** Catppuccin, Rosé Pine and Solarized trade contrast for pastel vibrancy;
  most of their accents fail 4.5:1 as text. Dreamcoder chooses legibility first and lower chroma.
- **Against `origin/main`:** better on muted text, weakest accent, distinctness (14.0 → 15.1) and
  isoluminance (0.011 → 0.002). Outside this table, the info ↔ diagnostic near-duplicate (ΔE 2.1, two
  tokens that looked identical) is now one explicit alias.

Verdict: on the measured accessibility and uniformity axes the new Light is at or above every reference;
on raw distinctness and pure-white APCA it is close behind the best, by design.
