import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.python_support import (
    ROOT,
    load_policy,
    validate_policy,
    validate_project_metadata,
    write_github_output,
)


def test_checked_in_policy_matches_project_metadata() -> None:
    policy = load_policy(ROOT / "python-support.json")

    validate_project_metadata(policy, ROOT / "pyproject.toml")

    assert policy.minimum == "3.8"
    assert policy.stable[-1] == "3.15"
    assert policy.prerelease == ["3.16-dev"]


def test_policy_rejects_a_gap_in_stable_versions() -> None:
    policy = load_policy(ROOT / "python-support.json")

    with pytest.raises(ValueError, match="contiguous"):
        validate_policy(replace(policy, stable=["3.8", "3.10"]))


def test_policy_rejects_a_skipped_prerelease() -> None:
    policy = load_policy(ROOT / "python-support.json")

    with pytest.raises(ValueError, match="immediately follow"):
        validate_policy(replace(policy, prerelease=["3.17-dev"]))


def test_github_outputs_are_derived_from_policy(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "python-support.json")
    output_path = tmp_path / "github-output"

    write_github_output(policy, output_path)

    assert output_path.read_text(encoding="utf-8").splitlines() == [
        'stable=["3.8","3.9","3.10","3.11","3.12","3.13","3.14","3.15"]',
        'prerelease=["3.16-dev"]',
    ]
