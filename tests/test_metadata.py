#!/usr/bin/env python3
"""Test custom chunk metadata in header"""

import teehistorian_py as th
import json
import tempfile
import os

def test_metadata_disabled_by_default():
    """Verify metadata is NOT included by default"""
    print("Testing metadata disabled by default...")

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.teehistorian') as f:
        filepath = f.name

    try:
        # Create a writer without enabling metadata
        writer = th.TeehistorianWriter()
        writer.save(filepath)

        # Read it back and check header
        with open(filepath, 'rb') as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        if '__teehistorian_py' in header_json:
            print("❌ FAIL: __teehistorian_py found in header when it shouldn't be")
            return False
        else:
            print("✅ PASS: __teehistorian_py not in header (default behavior)")
            return True
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_metadata_enabled():
    """Verify metadata IS included when enabled"""
    print("\nTesting metadata enabled...")

    # First register a custom chunk
    @th.chunk("12345678-1234-5678-1234-567812345678")
    class MyCustomChunk:
        """A test custom chunk"""
        player_id: int = th.field(format="varint", description="Player ID")
        message: str = th.field(format="string", description="Message text")

    th.register_global(MyCustomChunk)

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.teehistorian') as f:
        filepath = f.name

    try:
        # Create a writer WITH metadata enabled
        writer = th.TeehistorianWriter()
        writer.set_include_custom_chunk_metadata(True)
        writer.save(filepath)

        # Read it back and check header
        with open(filepath, 'rb') as f:
            data = f.read()

        parser = th.Teehistorian(data)
        header_str = parser.get_header_str()
        header_json = json.loads(header_str)

        if '__teehistorian_py' not in header_json:
            print("❌ FAIL: __teehistorian_py NOT found in header when it should be")
            return False

        metadata = header_json['__teehistorian_py']

        # Verify structure
        if 'version' not in metadata:
            print("❌ FAIL: Missing 'version' in metadata")
            return False

        if 'chunks' not in metadata:
            print("❌ FAIL: Missing 'chunks' in metadata")
            return False

        chunks = metadata['chunks']
        test_uuid = "12345678-1234-5678-1234-567812345678"

        if test_uuid not in chunks:
            print(f"❌ FAIL: Custom chunk {test_uuid} not found in metadata")
            print(f"   Found chunks: {list(chunks.keys())}")
            return False

        chunk_def = chunks[test_uuid]

        if chunk_def['name'] != 'MyCustomChunk':
            print(f"❌ FAIL: Wrong chunk name: {chunk_def['name']}")
            return False

        # Check fields - fields is a dict where keys are field names
        fields = chunk_def['fields']
        if len(fields) != 2:
            print(f"❌ FAIL: Wrong field count: {len(fields)}")
            return False

        # Check field names
        if 'player_id' not in fields or 'message' not in fields:
            print(f"❌ FAIL: Missing expected fields. Found: {list(fields.keys())}")
            return False

        # Check field types
        if fields['player_id']['type'] != 'i32':
            print(f"❌ FAIL: Wrong player_id type: {fields['player_id']['type']}")
            return False

        if fields['message']['type'] != 'str':
            print(f"❌ FAIL: Wrong message type: {fields['message']['type']}")
            return False

        print("✅ PASS: Metadata correctly included with custom chunk definition")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)
        th.unregister_global(test_uuid)


def test_cannot_change_metadata_after_writing():
    """Verify metadata setting cannot be changed after writing starts"""
    print("\nTesting metadata setting locked after writing...")

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.teehistorian') as f:
        filepath = f.name

    try:
        writer = th.TeehistorianWriter()

        # Trigger header writing by saving
        writer.save(filepath)

        # Now try to change metadata setting
        try:
            writer.set_include_custom_chunk_metadata(True)
            print("❌ FAIL: Should have raised error when changing metadata after writing")
            return False
        except Exception as e:
            if "after writing has started" in str(e):
                print("✅ PASS: Correctly prevented metadata change after writing started")
                return True
            else:
                print(f"❌ FAIL: Wrong error message: {e}")
                return False

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


if __name__ == "__main__":
    print("Testing custom chunk metadata feature\n" + "="*50)

    results = []
    results.append(test_metadata_disabled_by_default())
    results.append(test_metadata_enabled())
    results.append(test_cannot_change_metadata_after_writing())

    print("\n" + "="*50)
    if all(results):
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
