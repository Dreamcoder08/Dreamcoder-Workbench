# Superseded: implement-herdr-dreamcoder-themes

Status: **superseded** (2026-09-11). The obsolete implementation was removed.

## Why

This change targeted exactly `herdr 0.7.3` and shipped
`src/dreamcoder_theme/herdr_activation.py`: a transactional activation that
replaced the resolved `config.toml` with a regular file and rejected an existing
symlink selector. Two facts made it obsolete:

1. The installed runtime advanced past 0.7.3 (0.7.3 -> 0.8.0 -> 0.8.2 -> 0.9.0),
   so its exact-version gate could never pass on a current machine.
2. `docs/herdr.md` already documented a different, version-aware contract: the
   switcher selects the generated variant for the installed version, deploys it
   next to the selector, and manages only an absent selector or an existing
   symlink. That contract is now implemented.

`verify-report.md` also recorded a `fail` verdict (blocker: the 0.7.3 renderer
emitted a palette-driven `[ui].accent` that the activation validator rejected),
so the change could not archive as written.

## What replaced it

- `src/dreamcoder_theme/herdr_switch.py` — version-aware selector switcher. It
  uses the exact checked-in profile when present and falls back to the newest
  generated variant for a newer unprofiled version, after `herdr config check`
  accepts it.
- `tests/test_herdr_switch.py` — focused coverage for selection, selector
  handling, reload outcomes, and rollback.
- `scripts/herdr-theme-switch.sh` — thin caller used by `apply-theme-mode.sh`.

## Removed

- `src/dreamcoder_theme/herdr_activation.py`
- `tests/test_herdr_activation.py`

Kept unchanged: the versioned `DreamcoderHerdr/.../<version>/config.*.toml`
variants, `herdr_contract.py` profiles and `detect_profile`, and repository-only
generation in `sync_herdr_repo_variants()`. Only the obsolete activation
mechanism is gone; git history retains it if 0.7.3 support is ever revisited.
