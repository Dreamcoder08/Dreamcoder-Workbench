# T8 Benchmark — Dreamcoder Dark against reference dark themes (2026-11-27)

Same method as the Light benchmark (`odd/evidence/light-coherence/t14-benchmark.md`): the repository's own math, reference values transcribed from each published palette, numbers only. APCA is shown as magnitude (negative polarity on dark). Muted = Dreamcoder `comment`.

| System | Text WCAG / APCA | Muted WCAG / APCA | Accents ≥ 4.5 | Weakest accent | Min ΔE2000 | Accent L spread | Max accent chroma |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dreamcoder Dark (new) | 17.62 / 95 | 13.34 / 77 | 7/7 | 10.31 | 14.2 | 0.002 | 0.128 |
| Dreamcoder Dark (main) | 16.83 / 92 | 13.62 / 78 | 7/7 | 8.80 | 1.0 | 0.089 | 0.164 |
| GitHub Dark Default | 16.02 / 95 | 6.31 / 45 | 7/7 | 5.63 | 13.0 | 0.137 | 0.205 |
| Catppuccin Mocha | 11.34 / 80 | 7.37 / 56 | 7/7 | 7.08 | 14.1 | 0.164 | 0.130 |
| Tokyo Night | 10.59 / 74 | 2.76 / 19 | 7/7 | 6.46 | 13.3 | 0.101 | 0.159 |
| Rosé Pine | 13.39 / 87 | 5.48 / 41 | 6/7 | 3.38 | 19.9 | 0.315 | 0.156 |
| Dracula | 13.36 / 99 | 3.03 / 25 | 7/7 | 4.53 | 18.2 | 0.273 | 0.220 |

## Reading

- **Leads:** weakest accent 10.31:1 (best reference 7.08, Catppuccin Mocha); isoluminance 0.002 against 0.101 for
  the next best; all seven accents usable as text; chroma capped at 0.128 for OLED halation, the lowest here
  except Catppuccin. Against `origin/main`: mauve ↔ lavender went from ΔE 1.0 (indistinguishable) to 14.2.
- **Does not lead:** pigment distinctness 14.2 against Rosé Pine 19.9 and Dracula 18.2. They buy separation with
  higher chroma and weaker accents (3.38:1 and 4.53:1); Dreamcoder keeps legibility first.
- **Open weakness (recommendation, needs a decision):**
  - `comment` at 13.3:1 is far brighter than every reference (2.8–7.4:1). The ramp order is now correct, but the
    gap to `text` (17.6:1) is small, so comments still do not recede much.
  - Near-white text at 17.6:1 on pure OLED black risks halation for astigmatic readers. Lowering `text` to about
    15:1 and `comment` to about 7–8:1 would keep AAA while easing glare. Both values are bounded by existing
    guards (`test_canonical_loaders` subtle APCA, Qt disabled contrast), so a change needs a deliberate pass.
