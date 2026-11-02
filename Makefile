.PHONY: install test coverage build clean lint python-lint shell-lint type-check format adr

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov=dreamcoder_theme --cov-report=term-missing

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

lint: python-lint shell-lint type-check

python-lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

shell-lint:
	find scripts/ -name '*.sh' -exec shellcheck --shell=bash {} +

type-check:
	# Same pinned mypy, stubs and config as the commit hook; no global mypy needed.
	pre-commit run mypy --all-files

format:
	ruff format src/ tests/

adr:
	@echo "=== Architecture Decision Records ==="
	@ls docs/adr/*.md | while read f; do \
		echo "  $$(basename $$f) — $$(head -3 "$$f" | tail -1)"; \
	done
	@echo "Total: $$(ls docs/adr/*.md 2>/dev/null | wc -l) ADRs"
