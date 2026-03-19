#!/usr/bin/env python3
"""Test if reading and writing produces byte-for-byte identical files."""

import json
from pathlib import Path

import pytest
import teehistorian_py as th

TEST_FILE = Path("tests/000c81cc-0922-4150-97e9-cd8f9776eb8e.teehistorian")


@pytest.mark.skipif(not TEST_FILE.exists(), reason=f"Test file not found: {TEST_FILE}")
@pytest.mark.xfail(reason="Header JSON key ordering is not preserved during roundtrip")
def test_roundtrip_exact_match():
    """Parse a teehistorian file, rewrite it, and verify byte-for-byte match."""
    original_data = TEST_FILE.read_bytes()

    parser = th.Teehistorian(original_data)
    header_json = json.loads(parser.get_header_str())

    writer = th.TeehistorianWriter()
    for key, value in header_json.items():
        if not key.startswith("__"):
            if isinstance(value, (dict, list)):
                writer.set_header(key, json.dumps(value))
            else:
                writer.set_header(key, str(value))

    for chunk in parser:
        writer.write(chunk)

    output_data = writer.getvalue()
    assert original_data == output_data, (
        f"Files differ: original={len(original_data)} bytes, output={len(output_data)} bytes"
    )
