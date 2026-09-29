# Engineering quality pass

## Objective

Raise maintainability of the theme engine and the repo gates using measured
evidence, without changing behaviour: reduce the worst cyclomatic-complexity
hotspots, ratchet the coverage gate to the real level, and document publication.

## Problem (measured 2026-09-29)

- `mypy --strict`: clean (56 files). Coverage: 83% (gate is 40%). ruff: clean.
- radon cc worst offenders: `palette.validate_palette` E(34),
  `design_system.evaluate_contract` D(26), `design_system._parse_renderer_output`
  D(21), then C(13–19) in doctor, targets, audit, herdr renderer, repair, backups.
- Largest modules: `sync.py` 1061 lines, `cli_handlers.py` 620, `herdr_switch.py` 552.
- Coverage gate at 40% would let a 40-point regression through.

## Why

Central gates (contrast validation, design-system contract) with cyclomatic
complexity above 20 are hard to review and easy to break; a coverage floor far below
reality is not a gate.

## Scope

- In: behaviour-preserving extraction refactors of the three D/E functions (small
  pure helpers, no new abstractions beyond need), characterization tests written
  first where existing coverage of a branch is missing, coverage ratchet in
  `pyproject.toml` and CI, PR slicing plan for the stacked branches.
- Out: splitting `sync.py`/`cli_handlers.py` wholesale (separate design decision,
  in-flight `hexagonal-architecture-v2` change exists); pushing or opening PRs
  (user decision); changing any generated artifact byte.

## Constraints

- Public function signatures and outputs unchanged; every Light/Dark artifact
  byte-identical (`./scripts/dreamcoder sync` repo-only must report 0 changes).
- ruff, ruff format, `mypy --strict`, shellcheck stay clean.
- Never stage the unrelated timer-rewritten / user working-tree files.
- TDD: off (no project configuration). Runners: `python -m pytest tests/`,
  `bats tests/shell/ tests/ml4w/`. Complexity check: `uvx radon cc src -s -n C`.
- Delivery: work-unit commits on `refactor/remove-night-profile`.

## Tasks

- [x] Q0 — Resolve the SUPER+SHIFT+arrows overlap (variant resize vs profile move):
  resize moved to SUPER+CTRL+arrows, collision test has no exceptions. Route: inline.
- [x] Q1 — Refactor `validate_palette` (E→ at most B) preserving every error message and order. Route: delegated writer.
  `validate_palette` E(34) → B(6); helpers all ≤ B(8). Commits: 4c4214b (refactor),
  c4db159 (fail-fast/skip tests); characterization tests landed in 684026f (see note).
- [x] Q2 — Refactor `evaluate_contract` and `_parse_renderer_output` (D→ at most B). Route: delegated writer.
  `evaluate_contract` D(26) → A(1), `_parse_renderer_output` D(21) → A(2) via a per-target
  parser table; helpers all ≤ B(7). Commit: d503d2e.
- [x] Q3 — Ratchet coverage `fail_under` (pyproject + CI + ADR-0003) from 40 to 80 (measured 83–84%). Commit: 089f513. Route: inline.
- [x] Q4 — PR slicing plan (nothing pushed; user decides): keep commit order, cut at
  commit boundaries into chained PRs: (1) ML4W 2.16 compat f7c2b9b..339ab7e,
  (2) stow layer + Herdr 0.9.1 3398856..a7c925a, (3) theme-mode correctness + listener
  hook 702751f..8127674, (4) shell safety c9cf723..754d352, (5) Night removal
  319ffdd..f7597b1, (6) quality pass 089f513 onwards. PRs 1, 2, 3 and 5 exceed the
  ~400-line heuristic (tests, fixtures and generated deletions dominate); 684026f mixes
  characterization tests into the extract() fix, to be re-cut when slicing. Route: inline.
- [x] Q5 — Found while verifying Q1/Q2: `dreamcoder sync --help` ran a real sync.
  `main(argv)` now parses arguments before any side effect (--help exits 0, unknown
  options exit 2); tests inject argv. Route: inline.

## Acceptance criteria

- radon reports no function above C(15) in the three refactored areas; `validate_palette` at most B.
- Full pytest + bats green; repo-only sync reports 0 changes; mypy/ruff clean.

## Progress

- Baseline metrics above. Q0 done.
- Q1/Q2 evidence: characterization tests written first and green on the old code
  (golden ordered error list over a frozen dark palette; exact findings for
  MISSING_MODE, ROLE_RESOLUTION, RENDER_FAILURE, SEMANTIC_PROVENANCE_INVALID; parser
  invalid-JSON/unknown-target). The three functions are now 100% line-covered.
  Coverage total 83% → 84%. pytest exit 0; bats 147/147 ok; ruff, ruff format, mypy
  (56 files) clean. Byte identity: sync run in an isolated worktree with a throwaway
  HOME/XDG_* (`DREAMCODER_THEME_MODE=dark|light`, `DREAMCODER_WRITE_REPO=1`), sha256
  of all 900 tracked non-src files plus 20 HOME outputs identical HEAD vs refactor in
  both modes.
- Note: a concurrent commit (684026f `fix(shell): ...`) swept the staged
  characterization tests in with it; left as-is (no history rewrite). Later commits
  use `git commit --only <paths>`.
- Incident: `./scripts/dreamcoder sync --help` does not parse `--help` and ran a real
  sync once (active light identity re-applied to live paths; it also regenerated the
  timer-modified `DreamcoderPi/.../dreamcoder-dark.json` and
  `DreamcoderWarp/.../Dreamcoder-Dark.yaml` back to their committed bytes).

## Next step

Feature complete; publication is the user's decision.
