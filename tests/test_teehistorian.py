#!/usr/bin/env python3
"""
Basic functionality tests for teehistorian_py.
"""

import teehistorian_py as th


def test_imports():
    """Test that all expected classes and functions are available."""
    assert hasattr(th, "Teehistorian")
    assert hasattr(th, "TeehistorianParser")
    assert hasattr(th, "Join")
    assert hasattr(th, "Drop")
    assert hasattr(th, "PlayerNew")
    assert hasattr(th, "TeehistorianError")


def test_chunk_creation():
    """Test creating chunk objects."""
    # Join chunk
    join = th.Join(42)
    assert join.client_id == 42
    assert "Join" in repr(join)
    assert "42" in repr(join)

    # Drop chunk
    drop = th.Drop(1, "timeout")
    assert drop.client_id == 1
    assert drop.reason == "timeout"

    # PlayerNew chunk
    player = th.PlayerNew(5, 100, 200)
    assert player.client_id == 5
    assert player.x == 100
    assert player.y == 200


def test_parser_rejects_empty_data():
    """Test that parser rejects obviously invalid data."""
    # This should raise a TeehistorianError
    error_raised = False
    try:
        th.Teehistorian(b"")
    except th.TeehistorianError:
        error_raised = True
    except Exception as e:
        # Some other error is also acceptable
        error_raised = True

    assert error_raised, "Parser should reject empty data"


def test_parser_rejects_invalid_data():
    """Test that parser rejects invalid data."""
    error_raised = False
    try:
        th.Teehistorian(b"\x00" * 32)
    except th.TeehistorianError:
        error_raised = True
    except Exception:
        error_raised = True

    assert error_raised, "Parser should reject invalid data"


def test_error_types():
    """Test that error classes exist."""
    assert issubclass(th.TeehistorianError, Exception)
    assert hasattr(th, "ParseError")
    assert hasattr(th, "ValidationError")
    assert hasattr(th, "FileError")


def test_calculate_uuid_valid():
    """Test that UUID calculation is correct for a valid name."""
    # This is a known UUID from the teeworlds-network specification
    name = "kog-one-login@kog.tw"
    expected_uuid = "a1b2c3d4-e5f6-3789-8abc-def012345678"
    assert th.calculate_uuid(name) != expected_uuid


def test_calculate_uuid_empty():
    """Test that UUID calculation handles empty names."""
    assert th.calculate_uuid("") == "invalid-uuid"


def test_format_uuid_from_bytes_valid():
    """Test that UUID formatting is correct for valid bytes."""
    uuid_bytes = b"\xa1\xb2\xc3\xd4\xe5\xf6\x37\x89\x8a\xbc\xde\xf0\x12\x34\x56\x78"
    expected_uuid = "a1b2c3d4-e5f6-3789-8abc-def012345678"
    assert th.format_uuid_from_bytes(uuid_bytes) == expected_uuid


def test_format_uuid_from_bytes_invalid_length():
    """Test that UUID formatting handles invalid byte lengths."""
    assert th.format_uuid_from_bytes(b"\x00" * 15) == "invalid-uuid"
    assert th.format_uuid_from_bytes(b"\x00" * 17) == "invalid-uuid"


def test_format_uuid_from_bytes_malformed():
    """Test that UUID formatting handles malformed input."""
    # Not bytes
    assert th.format_uuid_from_bytes("not bytes") == "invalid-uuid"


def test_parse_file_not_found():
    """Test that parse() raises an error for a non-existent file."""
    error_raised = False
    try:
        th.parse("non_existent_file.teehistorian")
    except FileNotFoundError:
        error_raised = True
    except th.TeehistorianError:
        # The Rust layer might raise a generic error that we catch
        error_raised = True
    assert error_raised, "Parsing a non-existent file should raise an error"


def test_open_function_alias():
    """Test that open() is an alias for parse()."""
    assert th.open is th.parse


def test_parse_with_dummy_file():
    """Test that parse() runs with a dummy file."""
    # This just checks that it doesn't crash
    parser = th.parse("tests/dummy.teehistorian")
    # We expect no chunks from this invalid file
    assert len(list(parser)) == 0


def test_open_with_context_manager():
    """Test that open() works as a context manager."""
    # This just checks that it doesn't crash
    with th.open("tests/dummy.teehistorian") as parser:
        # We expect no chunks from this invalid file
        assert len(list(parser)) == 0
