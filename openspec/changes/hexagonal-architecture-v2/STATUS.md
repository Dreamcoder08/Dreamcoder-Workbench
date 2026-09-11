# Status: hexagonal-architecture-v2 (partially delivered)

Status: **open — partially delivered** (updated 2026-09-11). Not superseded; not
abandoned. This note records which requirements already landed so the remaining
scope is not misread as unstarted.

## Delivered by `reconcile-renderer-registry` (archived 2026-09-11-004)

The renderer-registry half of this change landed through the separate
`reconcile-renderer-registry` change, whose canonical spec now lives at
`openspec/specs/renderer-registry/spec.md`:

- **Formal renderer port** — `src/dreamcoder_theme/renderer_contract.py`.
- **Immutable declarative renderer registrations** —
  `src/dreamcoder_theme/renderer_registry.py`.
- **Renderer registry validation and purity** — `validate_registry()` plus the
  purity guarantees covered by `tests/test_renderer_registry.py`.
- **Exact consumer registry migration and bijection** — the assembled registry
  (33 consumers after the reconciliation) with `EXPECTED_CONSUMER_IDS` and the
  bijection/purity tests.
- **Adapter-bound specialized behavior** — `renderer_adapters.py` and the
  expected consumer-ID set.
- **Single declarative sync registry** and **ThemePaths facade** — pre-existing
  `VARIANT_REGISTRY` / `theme_paths` behavior, now described by the registry.

## Remaining scope (not started)

- `targets.json` canonical installer catalog.
- Manifest relationship clarity among rollout, renderer, and installer
  inventories.
- Derived Go, shell, and Python installer inventories with parity.
- Migration preflight and metadata normalization.
- Manifest schema, loader, parity, and drift tests.
- Contributor documentation for the above.

No later change re-attempted these. Resuming them is an explicit decision, not
an assumption of this note.
