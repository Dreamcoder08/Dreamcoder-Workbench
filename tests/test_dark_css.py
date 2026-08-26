import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = ROOT / "DreamcoderThemes" / "dreamcoder"
GENERATOR = ROOT / "scripts" / "generate-dark-css.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("dark_css_generator", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_css_exposes_canonical_dark_surfaces_aliases_and_guidance():
    generator = load_generator()
    tokens = json.loads((THEME_ROOT / "tokens.json").read_text(encoding="utf-8"))

    css = generator.render_css(tokens)

    assert ':root[data-theme="dark"] {' in css
    assert "--dc-bg: #000000;" in css
    assert "--dc-surface-scroll: #060608;" in css
    assert "--dc-surface-3: #1E1E24;" in css
    assert "--dc-border-subtle: #12121A;" in css
    assert "--dc-border-medium: #1F1F2B;" in css
    assert "--dc-text-primary: #E2E8F0;" in css
    assert "--dc-text-secondary: #94A3B8;" in css
    assert "--dc-text-muted: #64748B;" in css
    assert "--dc-accent-brand: #6366F1;" in css
    assert "--dc-error: #F87171;" in css
    assert "--dc-glow-focus:" in css
    assert "--dc-font-weight-heading: 600;" in css
    assert "Scrollable workspaces and editors" in css


def test_checked_in_css_matches_canonical_tokens():
    generator = load_generator()

    assert generator.check_generated() is None


def test_css_drift_check_is_read_only(tmp_path):
    generator = load_generator()
    output = tmp_path / "dreamcoder-dark.css"
    output.write_text("stale\n", encoding="utf-8")

    drift = generator.check_generated(generator.TOKENS_FILE, output)

    assert drift is not None
    assert "GENERATED_DRIFT:" in drift
    assert "python scripts/generate-dark-css.py" in drift
    assert output.read_text(encoding="utf-8") == "stale\n"
