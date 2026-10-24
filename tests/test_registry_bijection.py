"""Exact registry bijection tests (hexagonal-architecture-v2 task 1.6).

Proves the consumer-ID set equals the frozen original 33 plus GTK/Qt exactly —
no additions, omissions, or duplicates — and that special consumers are
adapter-backed while selector-only/excluded/scheduler/maintenance/unrelated
rollout records are absent. Sample-six or fixture-only coverage is not accepted.
"""

from __future__ import annotations

import json
from pathlib import Path

from dreamcoder_theme.renderer_contract import Renderer
from dreamcoder_theme.renderer_registry import (
    EXPECTED_CONSUMER_IDS,
    REGISTRATIONS,
    validate_registry,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
FROZEN_IDS = frozenset(
    json.loads((FIXTURES / "expected_consumer_ids.json").read_text())["expected_consumer_ids"]
)
TOOLKIT_IDS = frozenset({"gtk3", "gtk4", "qt6ct"})
EXPECTED_IDS = FROZEN_IDS | TOOLKIT_IDS

# Selector-only / excluded / scheduler / maintenance / unrelated rollout records
# from the 37-ID manifest that must NEVER appear as renderer registrations.
NON_RENDERER_ROLLOUT_RECORDS = {
    "dreamcoder-doctor-maintenance",
    "dreamcoder-dusk-runtime",
    "dreamcoder-unrelated-application-settings",
    "dreamcoder-scheduler",
    "dreamcoder-maintenance",
    "dreamcoder-selector-only",
}

SPECIAL_ADAPTER_CONSUMERS = {"opencode", "zellij", "nvim", "herdr"}


class TestExactBijection:
    def test_registered_ids_equal_expected_set_exactly(self) -> None:
        ids = {r.consumer_id for r in REGISTRATIONS}
        assert len(FROZEN_IDS) == 33
        assert FROZEN_IDS.isdisjoint(TOOLKIT_IDS)
        assert ids == EXPECTED_IDS
        assert ids == set(EXPECTED_CONSUMER_IDS)

    def test_no_duplicate_ids(self) -> None:
        ids = [r.consumer_id for r in REGISTRATIONS]
        assert len(ids) == len(set(ids)) == len(EXPECTED_IDS)

    def test_missing_id_produces_diagnostic(self) -> None:
        subset = tuple(r for r in REGISTRATIONS if r.consumer_id != "kitty")
        problems = validate_registry(subset)
        assert any("kitty" in p and "missing" in p for p in problems)

    def test_extra_id_produces_diagnostic(self) -> None:
        from dreamcoder_theme.renderer_contract import (  # noqa: PLC0415
            ActiveStrategy,
            MutationStrategy,
            RendererRegistration,
            RendererStrategy,
            RepositoryStrategy,
            SyncDefinition,
        )
        from dreamcoder_theme.renderers_kitty import kitty_content  # noqa: PLC0415

        extra = RendererRegistration(
            consumer_id="not-in-inventory",
            renderer=kitty_content,
            contract_version=1,
            modes=frozenset({"dark"}),
            output_kind="active",
            sync=SyncDefinition(
                renderer=RendererStrategy.DIRECT_CONTENT,
                active=ActiveStrategy.RESOLVED_ACTIVE_PATH,
                repository=RepositoryStrategy.NO_VARIANTS,
                mutation=MutationStrategy.WRITE_IF_CHANGED,
            ),
            summary_label="Extra",
        )
        problems = validate_registry((*REGISTRATIONS, extra))
        assert any("not-in-inventory" in p and "extra" in p for p in problems)


class TestSpecialConsumers:
    def test_special_consumers_present_exactly_once_via_adapters(self) -> None:
        registered = {r.consumer_id: r for r in REGISTRATIONS}
        assert set(registered) >= SPECIAL_ADAPTER_CONSUMERS
        for cid in SPECIAL_ADAPTER_CONSUMERS:
            assert isinstance(registered[cid].renderer, Renderer)

    def test_adapter_backed_special_consumers_render_str(self) -> None:
        from dreamcoder_theme.palette_tokens import VARIANTS  # noqa: PLC0415

        palette = dict(VARIANTS["dark"])
        registered = {r.consumer_id: r for r in REGISTRATIONS}
        for cid in SPECIAL_ADAPTER_CONSUMERS:
            for mode in registered[cid].modes:
                result = registered[cid].renderer(palette)
                assert type(result) is str, f"{cid} returned non-str for {mode}"


class TestExclusions:
    def test_non_renderer_rollout_records_are_absent(self) -> None:
        ids = {r.consumer_id for r in REGISTRATIONS}
        assert ids.isdisjoint(NON_RENDERER_ROLLOUT_RECORDS)

    def test_bijection_still_passes_without_rollout_records(self) -> None:
        assert validate_registry(REGISTRATIONS) == []
