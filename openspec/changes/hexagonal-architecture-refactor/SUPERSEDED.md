# Superseded: hexagonal-architecture-refactor

Status: **superseded** (2026-09-11). Its delivered scope landed; its remaining
plan is stale and owned by a successor.

## Why

This change's Phase 1 shell-library work has already landed: `lib/checks.sh`,
`lib/env.sh`, `lib/hyprland.sh`, `lib/logging.sh`, `lib/safety.sh`, and
`lib/theme.sh` exist and `scripts/` consumes them. The remainder of its broad
shell/Python rewrite plan was never resumed.

`hexagonal-architecture-v2` states this in its own proposal: it "uses that audit
only as evidence for the remaining Python renderer and installer gaps; it does
not resume or duplicate the earlier shell scope", and its Non-goals include
"resuming the archived July `hexagonal-architecture-refactor` or duplicating its
completed shell-library scope".

## Disposition

- **Delivered**: the Phase 1 shell library (`lib/`).
- **Superseded by**: `hexagonal-architecture-v2` for the remaining Python
  renderer and installer contracts.
- **Not resumed**: the original broad shell rewrite plan.

The original proposal, design, spec, and tasks are kept for their audit value;
they are not a plan of record.
