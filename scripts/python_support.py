#!/usr/bin/env python3
"""Validate and export the project's checked-in Python support policy."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
STABLE_VERSION = re.compile(r"^3\.(0|[1-9][0-9]*)$")
PRERELEASE_VERSION = re.compile(r"^3\.(0|[1-9][0-9]*)-dev$")
PYTHON_CLASSIFIER = re.compile(
    r'"Programming Language :: Python :: (3\.[0-9]+)"'
)
REQUIRES_PYTHON = re.compile(r'^requires-python\s*=\s*"([^"]+)"', re.MULTILINE)


@dataclass(frozen=True)
class SupportPolicy:
    minimum: str
    stable: List[str]
    prerelease: List[str]


def _minor(version: str, pattern: re.Pattern[str]) -> int:
    match = pattern.fullmatch(version)
    if match is None:
        raise ValueError("invalid Python version in support policy: {0}".format(version))
    return int(match.group(1))


def load_policy(path: Path) -> SupportPolicy:
    raw = json.loads(path.read_text(encoding="utf-8"))
    policy = SupportPolicy(
        minimum=raw["minimum"],
        stable=list(raw["stable"]),
        prerelease=list(raw.get("prerelease", [])),
    )
    validate_policy(policy)
    return policy


def validate_policy(policy: SupportPolicy) -> None:
    if not policy.stable:
        raise ValueError("support policy must contain at least one stable Python version")
    if policy.minimum != policy.stable[0]:
        raise ValueError("minimum Python version must be the first stable version")

    stable_minors = [_minor(version, STABLE_VERSION) for version in policy.stable]
    expected_stable = list(range(stable_minors[0], stable_minors[-1] + 1))
    if stable_minors != expected_stable:
        raise ValueError("stable Python versions must be contiguous from the minimum")

    prerelease_minors = [
        _minor(version, PRERELEASE_VERSION) for version in policy.prerelease
    ]
    expected_prerelease = list(
        range(stable_minors[-1] + 1, stable_minors[-1] + 1 + len(prerelease_minors))
    )
    if prerelease_minors != expected_prerelease:
        raise ValueError("prerelease Python versions must immediately follow stable support")


def validate_project_metadata(policy: SupportPolicy, pyproject_path: Path) -> None:
    pyproject = pyproject_path.read_text(encoding="utf-8")
    requires_python = REQUIRES_PYTHON.search(pyproject)
    expected_requirement = ">={0}".format(policy.minimum)
    if requires_python is None or requires_python.group(1) != expected_requirement:
        raise ValueError(
            "pyproject requires-python must be {0}".format(expected_requirement)
        )

    classifiers = PYTHON_CLASSIFIER.findall(pyproject)
    if classifiers != policy.stable:
        raise ValueError(
            "pyproject Python classifiers must exactly match stable support: {0}".format(
                ", ".join(policy.stable)
            )
        )


def write_github_output(policy: SupportPolicy, output_path: Path) -> None:
    stable = json.dumps(policy.stable, separators=(",", ":"))
    prerelease = json.dumps(policy.prerelease, separators=(",", ":"))
    with output_path.open("a", encoding="utf-8") as output:
        output.write("stable={0}\n".format(stable))
        output.write("prerelease={0}\n".format(prerelease))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=ROOT / "python-support.json")
    parser.add_argument("--pyproject", type=Path, default=ROOT / "pyproject.toml")
    parser.add_argument("--github-output", type=Path)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    policy = load_policy(args.policy)
    validate_project_metadata(policy, args.pyproject)
    if args.github_output is not None:
        write_github_output(policy, args.github_output)
    print(
        "required Python: {0}; experimental: {1}".format(
            ", ".join(policy.stable), ", ".join(policy.prerelease) or "none"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
