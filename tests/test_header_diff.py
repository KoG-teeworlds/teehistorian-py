#!/usr/bin/env python3
"""Analyze the header difference between original and roundtripped files."""

import json
from pathlib import Path

import pytest
import teehistorian_py as th

TEST_FILE = Path("tests/000c81cc-0922-4150-97e9-cd8f9776eb8e.teehistorian")


@pytest.mark.skipif(not TEST_FILE.exists(), reason=f"Test file not found: {TEST_FILE}")
def test_header_roundtrip_preserves_content():
    """Verify header content is preserved during roundtrip (ignoring key order)."""
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

    output_data = writer.getvalue()
    uuid_size = 16
    header_end = output_data.find(b"\x00", uuid_size)
    new_header_json = json.loads(output_data[uuid_size:header_end].decode("utf-8"))

    # Content should match even if key order differs
    assert header_json == new_header_json
