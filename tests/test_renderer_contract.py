"""Renderer port conformance tests (hexagonal-architecture-v2 tasks 1.1/1.2).

Proves that existing function-based leaf renderers satisfy the formal
``Renderer`` port without a class wrapper, that adapters present the same
single-port contract, and that there is exactly one renderer contract.
"""

from __future__ import annotations

import pytest

from dreamcoder_theme.palette_tokens import VARIANTS
from dreamcoder_theme.renderer_contract import (
    ALL_RENDER_VARIANTS,
    CANONICAL_MODES,
    Palette,
    Renderer,
)
from dreamcoder_theme.renderers_kitty import kitty_content

DARK: Palette = dict(VARIANTS["dark"])


def test_canonical_modes_are_distinct_from_derived_render_variants() -> None:
    assert {"light", "dusk", "dark"} == CANONICAL_MODES
    assert {"light", "dark", "night"} == ALL_RENDER_VARIANTS
    assert "night" not in CANONICAL_MODES
    assert "dusk" not in ALL_RENDER_VARIANTS


class TestFunctionRendererConformance:
    def test_leaf_function_satisfies_protocol_without_class_wrapper(self) -> None:
        """A plain dict[str, str] -> str function is a Renderer (no class)."""
        assert isinstance(kitty_content, Renderer)
        result = kitty_content(DARK)
        assert isinstance(result, str)
        assert "background" in result or "#" in result

    def test_any_plain_leaf_shape_conforms(self) -> None:
        def leaf(palette: Palette) -> str:
            return f"bg={palette['bg']}"

        renderer: Renderer = leaf
        assert isinstance(renderer(DARK), str)

    def test_renderer_protocol_returns_str(self) -> None:
        """The port requires exactly one palette mapping in, one str out."""
        assert Renderer.__call__ is not None
        for sample in (kitty_content,):
            out = sample(DARK)
            assert type(out) is str


class TestAdaptersUseTheSinglePort:
    @pytest.fixture(scope="class")
    @classmethod
    def adapters(cls):
        from dreamcoder_theme.herdr_contract import SUPPORTED_PROFILES  # noqa: PLC0415
        from dreamcoder_theme.renderer_adapters import (  # noqa: PLC0415
            NamedZellijAdapter,
            NvimDispatcherAdapter,
            TransparentOpenCodeAdapter,
            VersionedHerdrAdapter,
        )

        complete = next((p for p in SUPPORTED_PROFILES if p is not None and p.is_complete), None)
        if complete is None:
            pytest.skip("no complete Herdr profile available")
        return (
            TransparentOpenCodeAdapter(),
            NvimDispatcherAdapter(),
            NamedZellijAdapter("dreamcoder"),
            VersionedHerdrAdapter(complete, "night"),
        )

    def test_every_adapter_conforms_to_the_one_contract(self, adapters) -> None:
        """No second renderer signature: each adapter is a Renderer."""
        for adapter in adapters:
            assert isinstance(adapter, Renderer)

    def test_every_adapter_accepts_one_palette_and_returns_str(self, adapters) -> None:
        for adapter in adapters:
            out = adapter(DARK)
            assert type(out) is str
