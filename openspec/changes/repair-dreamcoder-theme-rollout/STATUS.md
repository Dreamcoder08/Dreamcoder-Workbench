# Status: repair-dreamcoder-theme-rollout (Slice 1A only)

Status: **open — only the first slice landed** (updated 2026-09-11).

## Delivered (5/62) — Slice 1A

- `DreamcoderThemes/dreamcoder/targets.json` and `DreamcoderThemes/dreamcoder/targets.schema.json` —
  the required-target manifest.
- `src/dreamcoder_theme/targets.py` — the narrow manifest model API.
- Manifest tests plus valid / missing-field / duplicate / excluded / `dusk` / incomplete-audit fixtures.
- The completed Ghostty 1.3.1-arch2 title-field remediation is preserved as historical evidence.

## Remaining (57) — unstarted slices

- Slice 1B — inventory parity adapters.
- Slice 1C — token parity and readability diagnostics.
- Slice 2 — Nytherx dark calibration with light byte baseline.
- Slice 3 — deterministic terminal and shell generation.
- Slice 4 — editor, CLI, desktop, and ML4W output parity.
- The remaining rollout classification, ownership, switching idempotence, Herdr, and Ghostty
  requirements.

This is a 62-task plan; only its first slice landed. Whether to resume it is an explicit decision,
not an assumption of this note.
