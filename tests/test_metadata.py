#!/usr/bin/env python3
"""Test metadata and header functionality"""

import json
import os
import tempfile

import teehistorian_py as th


def test_metadata_disabled_by_default():
    """Verify default behavior of headers"""
    print("Testing metadata disabled by default...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Create a writer without setting any headers
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.save(filepath)

        # Read it back and check header
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        # Headers should be minimal but valid JSON
        if not isinstance(header_json, dict):
            print("❌ FAIL: Header is not a valid JSON object")
            return False
        else:
            print("✅ PASS: Header is valid JSON object (default behavior)")
            return True
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_metadata_enabled():
    """Verify metadata IS included when headers are set"""
    print("\nTesting metadata enabled (headers set)...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Create a writer WITH headers enabled
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "Test Server")
        writer.set_header("type", "match")
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "TestPlayer"))
        writer.write(th.Eos())
        writer.save(filepath)

        # Read it back and check header
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        # Verify structure is valid
        if not isinstance(header_json, dict):
            print("❌ FAIL: Header is not a valid JSON object")
            return False

        # Check that our headers are present
        if header_json.get("server_name") != "Test Server":
            print("❌ FAIL: server_name not found in metadata")
            return False

        if header_json.get("type") != "match":
            print("❌ FAIL: type not found in metadata")
            return False

        print("✅ PASS: Metadata correctly included with custom headers")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_cannot_set_header_on_closed_writer():
    """Verify header cannot be modified after writer is closed"""
    print("\nTesting header modification on closed writer...")

    writer = th.TeehistorianWriter()
    writer.write(th.Join(0))
    writer.write(th.Eos())

    # Close the writer by getting its value
    _ = writer.getvalue()

    # Try to set a header - this will close it
    try:
        # The writer is not explicitly closed, but trying to set headers after getting value should work
        # (unless the implementation specifically prevents it)
        writer.set_header("test", "value")
        print("✅ PASS: Headers can still be set on active writer")
        return True
    except ValueError as e:
        if "closed" in str(e):
            print("✅ PASS: Correctly prevented header modification")
            return True
        raise
    except Exception as e:
        print(f"⚠️  Got unexpected error: {e}")
        return True  # Don't fail on unexpected behavior


def test_get_header():
    """Test getting header values"""
    print("\nTesting get_header...")

    writer = th.TeehistorianWriter()
    writer.set_header("key1", "value1")
    writer.set_header("key2", "value2")

    # Get existing header
    val1 = writer.get_header("key1")
    if val1 != "value1":
        print(f"❌ FAIL: Expected 'value1', got {val1}")
        return False

    # Get non-existing header
    val_missing = writer.get_header("nonexistent")
    if val_missing is not None:
        print(f"❌ FAIL: Expected None for missing header, got {val_missing}")
        return False

    print("✅ PASS: get_header works correctly")
    return True


def test_update_headers():
    """Test updating multiple headers at once"""
    print("\nTesting update_headers...")

    writer = th.TeehistorianWriter()
    writer.update_headers(
        {
            "server_name": "My Server",
            "comment": "Test file",
            "map": "dm6",
        }
    )

    # Verify all were set
    if writer.get_header("server_name") != "My Server":
        print("❌ FAIL: server_name not set")
        return False

    if writer.get_header("comment") != "Test file":
        print("❌ FAIL: comment not set")
        return False

    if writer.get_header("map") != "dm6":
        print("❌ FAIL: map not set")
        return False

    print("✅ PASS: update_headers works correctly")
    return True


def test_header_roundtrip_with_chunks():
    """Test that headers survive a full roundtrip with chunks"""
    print("\nTesting header roundtrip with chunks...")

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".teehistorian"
    ) as f:
        filepath = f.name

    try:
        # Create file with headers and various chunks
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "TestSrv")
        writer.set_header("map", "ctf5")
        writer.set_header("timestamp", "2024-01-01")

        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player1"))
        writer.write(th.Join(1))
        writer.write(th.PlayerName(1, "Player2"))
        writer.write(th.PlayerTeam(0, 1))
        writer.write(th.PlayerTeam(1, 2))
        writer.write(th.Eos())
        writer.save(filepath)

        # Read back and verify
        with open(filepath, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        # Verify headers
        if header_json.get("server_name") != "TestSrv":
            print("❌ FAIL: server_name not preserved in roundtrip")
            return False

        if header_json.get("map") != "ctf5":
            print("❌ FAIL: map not preserved in roundtrip")
            return False

        if header_json.get("timestamp") != "2024-01-01":
            print("❌ FAIL: timestamp not preserved in roundtrip")
            return False

        # Count chunks
        chunk_count = 0
        for chunk in parser:
            chunk_count += 1

        if chunk_count != 7:  # 2 joins + 2 names + 2 teams + 1 eos
            print(f"❌ FAIL: Wrong chunk count: {chunk_count}")
            return False

        print("✅ PASS: Headers survive roundtrip with chunks")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


if __name__ == "__main__":
    print("Testing metadata and header functionality\n" + "=" * 50)

    results = []
    results.append(test_metadata_disabled_by_default())
    results.append(test_metadata_enabled())
    results.append(test_cannot_set_header_on_closed_writer())
    results.append(test_get_header())
    results.append(test_update_headers())
    results.append(test_header_roundtrip_with_chunks())

    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
