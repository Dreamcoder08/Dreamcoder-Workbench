"""Tests for the version-bound Herdr runtime compatibility profile."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dreamcoder_theme.herdr_contract import (
    HERDR_073_PROFILE,
    HERDR_080_PROFILE,
    HERDR_082_PROFILE,
    HERDR_091_PROFILE,
    SUPPORTED_PROFILES,
    ContractEvidence,
    ContractStatus,
    detect_profile,
    profile_from_evidence,
)
from dreamcoder_theme.renderers_herdr import (
    REGISTRATIONS,
    HerdrContractUnavailableError,
    herdr_content,
)

FIXTURES = Path(__file__).parent / "fixtures" / "herdr"


def load_evidence(name: str) -> ContractEvidence:
    try:
        contents = (FIXTURES / name).read_text()
        return ContractEvidence.from_mapping(json.loads(contents))
    except (OSError, json.JSONDecodeError) as error:
        pytest.fail(f"invalid Herdr test fixture {name}: {error}")


def test_complete_synthetic_profile_is_accepted_for_its_exact_version() -> None:
    profile = profile_from_evidence(load_evidence("complete-test-profile-0.7.3.json"))

    assert profile.is_complete
    selection = detect_profile("herdr 0.7.3", profiles=(profile,))
    assert selection.status is ContractStatus.SUPPORTED


def test_complete_synthetic_080_profile_is_accepted_for_its_exact_version() -> None:
    profile = profile_from_evidence(load_evidence("complete-test-profile-0.8.0.json"))

    assert profile.is_complete
    selection = detect_profile("herdr 0.8.0", profiles=(profile,))
    assert selection.status is ContractStatus.SUPPORTED


def test_production_080_profile_is_complete_and_version_bound() -> None:
    assert HERDR_080_PROFILE.is_complete
    assert detect_profile("herdr 0.8.0").profile is HERDR_080_PROFILE
    assert detect_profile("herdr 0.8.1").status is ContractStatus.UNSUPPORTED_CONTRACT


def test_source_derived_082_profile_is_complete_and_version_bound() -> None:
    assert HERDR_082_PROFILE.is_complete
    assert HERDR_082_PROFILE.evidence.source_sha256 == (
        "9d7bdfdb391d12112e7d4eb1bd3895e50bdb6556255ef75e634094a969684e2d"
    )
    assert detect_profile("herdr 0.8.2").profile is HERDR_082_PROFILE
    assert detect_profile("herdr 0.8.3").status is ContractStatus.UNSUPPORTED_CONTRACT


def test_installed_binary_091_profile_is_complete_and_version_bound() -> None:
    assert HERDR_091_PROFILE.is_complete
    assert HERDR_091_PROFILE.evidence.source_sha256 == (
        "2a02fed16beb651ef006e1d43f048f652ca4dc58ad053cd2d44450563d5c54b7"
    )
    assert HERDR_091_PROFILE.evidence.light_base_theme_name == "catppuccin-latte"
    assert detect_profile("herdr 0.9.1").profile is HERDR_091_PROFILE
    assert detect_profile("herdr 0.9.0").status is ContractStatus.UNSUPPORTED_CONTRACT
    assert detect_profile("herdr 0.9.2").status is ContractStatus.UNSUPPORTED_CONTRACT


def test_073_and_080_profiles_select_their_own_exact_versions() -> None:
    assert detect_profile("herdr 0.7.3").profile is HERDR_073_PROFILE
    assert detect_profile("herdr 0.8.0").profile is HERDR_080_PROFILE
    assert detect_profile("herdr 0.7.4").status is ContractStatus.UNSUPPORTED_CONTRACT


def test_production_profile_is_complete_and_version_bound() -> None:
    assert HERDR_073_PROFILE.is_complete
    assert detect_profile("herdr 0.7.3").profile is HERDR_073_PROFILE
    assert detect_profile("herdr 0.7.4").status is ContractStatus.UNSUPPORTED_CONTRACT


@pytest.mark.parametrize(
    ("version_output", "expected"),
    [
        (None, ContractStatus.SKIPPED_NOT_INSTALLED),
        ("herdr 0.7.4", ContractStatus.UNSUPPORTED_CONTRACT),
        ("not a version", ContractStatus.UNSUPPORTED_CONTRACT),
    ],
)
def test_absent_unknown_and_malformed_runtime_evidence_is_not_supported(
    version_output: str | None, expected: ContractStatus
) -> None:
    selection = detect_profile(version_output, profiles=())
    assert selection.status is expected


@pytest.mark.parametrize(
    "version_output",
    (
        "herdr 0.8.2-rc1",
        "herdr 0.8.2+build.7",
        "herdr 0.8.2unexpected",
        "wrapper: herdr 0.8.2",
        "herdr 0.8.2 extra",
    ),
)
def test_version_output_suffixes_and_embedding_fail_closed(version_output: str) -> None:
    assert detect_profile(version_output).status is ContractStatus.UNSUPPORTED_CONTRACT


@pytest.mark.parametrize(
    "version_output",
    ("herdr 0.8.2", "  HERDR 0.8.2  ", "\therdr\t0.8.2\n"),
)
def test_exact_version_output_allows_case_and_surrounding_whitespace(version_output: str) -> None:
    assert detect_profile(version_output).profile is HERDR_082_PROFILE


def test_rejected_version_fixture_cannot_enable_an_unsupported_runtime() -> None:
    profile = profile_from_evidence(load_evidence("herdr-0.7.2-rejected-version.json"))

    assert not profile.is_complete
    selection = detect_profile("herdr 0.7.2", profiles=(profile,))
    assert selection.status is ContractStatus.UNSUPPORTED_CONTRACT


def test_incomplete_073_evidence_remains_disabled() -> None:
    profile = profile_from_evidence(load_evidence("herdr-0.7.3-incomplete-evidence.json"))

    assert not profile.is_complete
    selection = detect_profile("herdr 0.7.3", profiles=(profile,))
    assert selection.status is ContractStatus.UNSUPPORTED_CONTRACT


def test_ambiguous_validation_or_reload_semantics_make_profile_incomplete() -> None:
    validation_ambiguous = profile_from_evidence(
        load_evidence("herdr-0.7.3-ambiguous-validation.json")
    )
    reload_ambiguous = profile_from_evidence(load_evidence("herdr-0.7.3-ambiguous-reload.json"))

    assert not validation_ambiguous.is_complete
    assert not reload_ambiguous.is_complete


def test_incomplete_profile_cannot_render() -> None:
    incomplete = profile_from_evidence(load_evidence("herdr-0.7.3-incomplete-evidence.json"))

    with pytest.raises(HerdrContractUnavailableError, match="complete profile"):
        herdr_content(incomplete, "dark", {"accent": "#abcdef"})


def test_registry_summary_label_tracks_live_supported_profiles() -> None:
    herdr = next(
        registration for registration in REGISTRATIONS if registration.consumer_id == "herdr"
    )
    versions = ", ".join(
        profile.evidence.version
        for profile in SUPPORTED_PROFILES
        if profile and profile.is_complete
    )

    assert herdr.summary_label == f"Herdr repository profiles ({versions})"
