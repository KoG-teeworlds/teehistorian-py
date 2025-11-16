#!/usr/bin/env python3
"""
Performance benchmarks for teehistorian_py.

Run with: pytest benchmarks/ --benchmark-only
"""

import pytest

# Placeholder benchmark - replace with actual benchmarks when test data is available


def test_placeholder_benchmark(benchmark):
    """Placeholder benchmark to ensure CI pipeline works."""

    def placeholder_function():
        # Simulate some work
        return sum(range(1000))

    result = benchmark(placeholder_function)
    assert result == 499500


# TODO: Add real benchmarks:
# - Parsing teehistorian files of various sizes
# - Chunk conversion performance
# - Iterator performance
# - Memory usage benchmarks
