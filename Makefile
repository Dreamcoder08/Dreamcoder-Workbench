.PHONY: install test coverage build clean lint python-lint shell-lint type-check format adr theme-check theme-diff specimen

# Interpreter for the theme regression targets (e.g. make theme-check PYTHON="uv run --quiet python").
PYTHON ?= python
# Base of the perceptual diff.
REF ?= origin/main

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

# Theme regression gate: regenerate every output from tokens.json, require that it
# matches the index (stage intentional changes first), then run the theme gates.
# The wallpaper step checks DreamcoderWallpapers/dreamcoder-{light,dark}-*.png per mode, skipped when
# the canonical set is absent.
# One mode per call: the mode is part of the canonical file name.
check_wallpapers = set -- DreamcoderWallpapers/dreamcoder-$(1)-*.png; if [ -e "$$1" ]; then $(PYTHON) scripts/check-wallpaper.py --mode $(1) "$$@"; else echo "check-wallpaper: no canonical $(1) wallpapers, skipped"; fi

theme-check:
	DREAMCODER_WRITE_LIVE=0 DREAMCODER_THEME_MODE=dark PYTHONPATH=src $(PYTHON) scripts/sync-dreamcoder-theme.py
	DREAMCODER_WRITE_LIVE=0 DREAMCODER_THEME_MODE=light PYTHONPATH=src $(PYTHON) scripts/sync-dreamcoder-theme.py
	git diff --exit-code
	PYTHONPATH=src $(PYTHON) scripts/verify-theme-health.py
	$(PYTHON) -m pytest -q -p no:cacheprovider -o addopts="" tests/test_light_*.py tests/test_token_*.py tests/test_apca_*.py tests/test_wallpaper_contract.py tests/test_theme_*.py
	$(call check_wallpapers,light)
	$(call check_wallpapers,dark)

theme-diff:
	$(PYTHON) scripts/theme-diff.py $(REF)

specimen:
	$(PYTHON) scripts/generate-specimen.py
