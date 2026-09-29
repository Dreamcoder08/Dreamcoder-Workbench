# ADR-003: Python Quality Strategy

## Status

Accepted

## Context

The Python codebase (`src/dreamcoder_theme/`) had no automated quality gates
beyond basic syntax correctness. As the package grew to 30+ modules, the lack
of type checking, consistent formatting, and coverage enforcement led to
preventable defects and made refactoring risky.

## Decision

We adopt a three-layer quality strategy for all Python code:

### Layer 1 — Ruff (linter + formatter)

- **Lint rules**: E, F, I, N, W, UP, YTT, ASYNC, SIM, PL, RUF
- **Line length**: 100 (overrides PEP 8 default of 79)
- **Formatter**: `ruff format` (Black-compatible)
- **Enforcement**: `ruff check` and `ruff format --check` must pass in CI

### Layer 2 — Mypy (type checker)

- **Mode**: Strict (`strict = true`)
- **Location**: `[tool.mypy]` in `pyproject.toml`
- **Overrides**: `PyQt6.*` and `matugen.*` get `ignore_missing_imports = true`
  (no stubs available)
- **Enforcement**: `mypy src/` must pass before merge

### Layer 3 — Coverage (pytest-cov)

- **Metric**: Branch coverage via `pytest --cov=dreamcoder_theme`
- **Threshold**: `fail_under = 80` (ratcheted from the original 40 baseline on 2026-09-29, when measured coverage was 83%; raise it again only when coverage rises — never lower it)
- **Reporting**: `--cov-report=term-missing` shows uncovered lines

All three layers run in CI on every push and pull request.

### Pre-commit integration

Ruff (lint + format) and Mypy run as pre-commit hooks via `.pre-commit-config.yaml`,
providing instant feedback before CI.

## Consequences

Positive:
- Type errors caught before runtime — safer refactoring
- Consistent code style across all contributors
- Coverage threshold prevents untested code from reaching main

Negative:
- Mypy strict mode requires explicit annotations throughout the codebase
- The 80% floor sits just under the measured level (83%), so a large untested addition fails CI; raising it is a deliberate follow-up
- Initial migration required fixing pre-existing issues

## Compliance

- `ruff check src/ tests/` must pass
- `ruff format --check src/ tests/` must pass
- `mypy src/` must pass (strict mode)
- `pytest --cov=dreamcoder_theme --cov-fail-under=80` must pass

## Alternatives Considered

- **Pyright/Pylance**: Rejected in favor of Mypy — more widely adopted in
  open-source Python, standard for PEP 484 compliance
- **Black**: Rejected for formatting — Ruff's built-in formatter is compatible
  and reduces dependency count
- **Flake8 + isort**: Replaced by Ruff — single tool, 10-100x faster
