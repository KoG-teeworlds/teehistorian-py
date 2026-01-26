#!/usr/bin/env python3
"""Test metadata roundtrip: write with metadata, read and verify"""

import json
import os
import tempfile

import teehistorian_py as th


def test_metadata_roundtrip_basic():
    """Write a file with metadata, then read it back and verify basic structure"""
    print("Testing metadata roundtrip (basic)...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Write a file with some chunks
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "Test Server")
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player 1"))
        writer.write(th.Eos())
        writer.save(filepath)

        # Read it back
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()

        # Verify header was preserved
        if "server_name" not in header_str:
            print("❌ FAIL: Header not preserved")
            return False

        # Verify we can iterate chunks
        chunk_count = 0
        for chunk in parser:
            chunk_count += 1

        if chunk_count != 3:  # Join + PlayerName + Eos
            print(f"❌ FAIL: Wrong chunk count: {chunk_count}")
            return False

        print("✅ PASS: Metadata roundtrip successful")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_no_metadata_no_registration():
    """Verify files without metadata don't cause issues"""
    print("\nTesting file without metadata...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Write a file
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.save(filepath)

        # Open it - should work fine
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)

        # Should be able to parse chunks
        chunk_count = 0
        for chunk in parser:
            chunk_count += 1

        if chunk_count != 2:  # Join + Eos
            print(f"❌ FAIL: Wrong chunk count: {chunk_count}")
            return False

        print("✅ PASS: Files work correctly")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_header_preservation():
    """Test that headers are properly preserved"""
    print("\nTesting header preservation...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Write with multiple headers
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "My Server")
        writer.set_header("comment", "Test comment")
        writer.set_header("version", "1.0")
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.save(filepath)

        # Read back
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)

        # Get header as JSON
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        # Verify all headers are present
        if header_json.get("server_name") != "My Server":
            print("❌ FAIL: server_name not preserved")
            return False

        if header_json.get("comment") != "Test comment":
            print("❌ FAIL: comment not preserved")
            return False

        if header_json.get("version") != "1.0":
            print("❌ FAIL: version not preserved")
            return False

        print("✅ PASS: Headers properly preserved")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


if __name__ == "__main__":
    print("Testing metadata roundtrip functionality\n" + "=" * 50)

    results = []
    results.append(test_metadata_roundtrip_basic())
    results.append(test_no_metadata_no_registration())
    results.append(test_header_preservation())

    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
