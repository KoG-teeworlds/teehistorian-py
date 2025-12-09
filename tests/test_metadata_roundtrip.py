#!/usr/bin/env python3
"""Test metadata roundtrip: write with metadata, read and verify auto-registration"""

import teehistorian_py as th
import tempfile
import os

def test_metadata_roundtrip():
    """Write a file with metadata, then read it back and verify auto-registration"""
    print("Testing metadata roundtrip...")

    # Define and register a custom chunk
    @th.chunk("aaaabbbb-cccc-dddd-eeee-ffffffff0000")
    class TestChunk:
        player_id: int = th.field(format="varint", description="Player ID")
        score: int = th.field(format="i32", description="Player score")
        nickname: str = th.field(format="string", description="Player nickname")

    # Register it
    th.register_global(TestChunk)

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.teehistorian') as f:
        filepath = f.name

    try:
        # Write a file with metadata enabled
        writer = th.TeehistorianWriter()
        writer.set_include_custom_chunk_metadata(True)
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.save(filepath)

        # Unregister the chunk to verify it gets re-registered from metadata
        th.unregister_global("aaaabbbb-cccc-dddd-eeee-ffffffff0000")
        registered = th.list_registered()
        if "aaaabbbb-cccc-dddd-eeee-ffffffff0000" in registered:
            print("❌ FAIL: Chunk still registered after unregister")
            return False

        # Now open the file - it should auto-register the chunk
        with open(filepath, 'rb') as f:
            data = f.read()

        parser = th.Teehistorian(data)

        # Verify the chunk was auto-registered
        registered = th.list_registered()
        if "aaaabbbb-cccc-dddd-eeee-ffffffff0000" not in registered:
            print(f"❌ FAIL: Chunk not auto-registered from metadata")
            print(f"   Registered UUIDs: {registered}")
            return False

        # Verify the chunk definition was restored
        chunk_def = th.get_global_chunk("aaaabbbb-cccc-dddd-eeee-ffffffff0000")
        if chunk_def is None:
            print("❌ FAIL: Chunk definition not found after auto-registration")
            return False

        if chunk_def.name != "TestChunk":
            print(f"❌ FAIL: Wrong chunk name: {chunk_def.name}")
            return False

        if len(chunk_def.fields) != 3:
            print(f"❌ FAIL: Wrong field count: {len(chunk_def.fields)}")
            return False

        field_names = [f.name for f in chunk_def.fields]
        if "player_id" not in field_names or "score" not in field_names or "nickname" not in field_names:
            print(f"❌ FAIL: Missing fields. Found: {field_names}")
            return False

        print("✅ PASS: Metadata roundtrip successful - chunk auto-registered from file")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)
        # Clean up registration
        th.unregister_global("aaaabbbb-cccc-dddd-eeee-ffffffff0000")


def test_no_metadata_no_registration():
    """Verify files without metadata don't cause issues"""
    print("\nTesting file without metadata...")

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.teehistorian') as f:
        filepath = f.name

    try:
        # Write a file WITHOUT metadata
        writer = th.TeehistorianWriter()
        # Don't enable metadata
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.save(filepath)

        # Open it - should work fine without metadata
        with open(filepath, 'rb') as f:
            data = f.read()

        parser = th.Teehistorian(data)

        # Should be able to parse chunks
        chunk_count = 0
        for chunk in parser:
            chunk_count += 1

        if chunk_count != 2:  # Join + Eos
            print(f"❌ FAIL: Wrong chunk count: {chunk_count}")
            return False

        print("✅ PASS: Files without metadata work correctly")
        return True

    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


if __name__ == "__main__":
    print("Testing metadata roundtrip functionality\n" + "="*50)

    results = []
    results.append(test_metadata_roundtrip())
    results.append(test_no_metadata_no_registration())

    print("\n" + "="*50)
    if all(results):
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
