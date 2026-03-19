#!/usr/bin/env python3
"""
Performance benchmarks for teehistorian_py.

Run with: pytest benchmarks/ --benchmark-only -v
"""

import pytest
from pathlib import Path

import teehistorian_py as th

TEST_FILE = Path(__file__).parent.parent / "tests" / "000c81cc-0922-4150-97e9-cd8f9776eb8e.teehistorian"

file_missing = pytest.mark.skipif(
    not TEST_FILE.exists(),
    reason=f"Test file not found: {TEST_FILE}",
)


@pytest.fixture(scope="module")
def test_file_bytes():
    """Load the test teehistorian file bytes once per module."""
    if not TEST_FILE.exists():
        pytest.skip(f"Test file not found: {TEST_FILE}")
    return TEST_FILE.read_bytes()


@pytest.fixture(scope="module")
def first_1000_chunks(test_file_bytes):
    """Parse and collect the first 1000 chunks from the test file."""
    parser = th.TeehistorianParser(test_file_bytes)
    chunks = []
    for i, chunk in enumerate(parser):
        if i >= 1000:
            break
        chunks.append(chunk)
    return chunks


@file_missing
def test_parse_file(benchmark, test_file_bytes):
    """Benchmark: parse the full test teehistorian file and iterate all chunks."""

    def parse_all():
        parser = th.TeehistorianParser(test_file_bytes)
        count = 0
        for _chunk in parser:
            count += 1
        return count

    count = benchmark(parse_all)
    assert count > 0


@file_missing
def test_parse_and_count_by_type(benchmark, test_file_bytes):
    """Benchmark: parse file and count chunks by type using isinstance checks."""

    def parse_and_count():
        parser = th.TeehistorianParser(test_file_bytes)
        counts = {
            "join": 0,
            "drop": 0,
            "player_diff": 0,
            "player_name": 0,
            "eos": 0,
            "other": 0,
        }
        for chunk in parser:
            if isinstance(chunk, th.Join):
                counts["join"] += 1
            elif isinstance(chunk, th.Drop):
                counts["drop"] += 1
            elif isinstance(chunk, th.PlayerDiff):
                counts["player_diff"] += 1
            elif isinstance(chunk, th.PlayerName):
                counts["player_name"] += 1
            elif isinstance(chunk, th.Eos):
                counts["eos"] += 1
            else:
                counts["other"] += 1
        return counts

    counts = benchmark(parse_and_count)
    total = sum(counts.values())
    assert total > 0


def test_write_chunks(benchmark):
    """Benchmark: create a writer, write 1000 Join/PlayerDiff/Eos chunks, call getvalue()."""

    def write_chunks():
        writer = th.TeehistorianWriter()
        # Write 333 cycles of Join + PlayerDiff + Eos pattern (= 999 chunks) + final Eos
        for i in range(333):
            writer.write(th.Join(i % 64))
            writer.write(th.PlayerDiff(i % 64, i % 100, i % 50))
            writer.write(th.Eos())
        writer.write(th.Eos())
        return writer.getvalue()

    data = benchmark(write_chunks)
    assert isinstance(data, bytes)
    assert len(data) > 0


@file_missing
def test_roundtrip(benchmark, test_file_bytes, first_1000_chunks):
    """Benchmark: parse first 1000 chunks, write to new writer, verify output bytes."""

    def roundtrip():
        writer = th.TeehistorianWriter()
        for chunk in first_1000_chunks:
            writer.write(chunk)
        return writer.getvalue()

    data = benchmark(roundtrip)
    assert isinstance(data, bytes)
    assert len(data) > 0
