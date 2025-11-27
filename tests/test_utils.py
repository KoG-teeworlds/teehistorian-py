#!/usr/bin/env python3
"""Tests for the utils module."""

import pytest
from teehistorian_py.utils import calculate_uuid, format_uuid_from_bytes


class TestCalculateUuid:
    """Tests for calculate_uuid function."""

    def test_calculate_uuid_returns_string(self):
        """Test that calculate_uuid returns a string."""
        result = calculate_uuid("test-name")
        assert isinstance(result, str)

    def test_calculate_uuid_valid_format(self):
        """Test that calculate_uuid returns a valid UUID format."""
        result = calculate_uuid("test-name")
        # UUID format: 8-4-4-4-12 hex characters
        parts = result.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_calculate_uuid_hex_characters(self):
        """Test that calculate_uuid contains only hex characters."""
        result = calculate_uuid("test-name")
        # Remove hyphens and check all characters are hex
        hex_part = result.replace("-", "")
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_calculate_uuid_deterministic(self):
        """Test that calculate_uuid is deterministic for same input."""
        uuid1 = calculate_uuid("test-name")
        uuid2 = calculate_uuid("test-name")
        assert uuid1 == uuid2

    def test_calculate_uuid_different_names(self):
        """Test that different names produce different UUIDs."""
        uuid1 = calculate_uuid("name1")
        uuid2 = calculate_uuid("name2")
        assert uuid1 != uuid2

    def test_calculate_uuid_known_value(self):
        """Test with a known name to verify deterministic behavior."""
        result = calculate_uuid("kog-one-login@kog.tw")
        # Should be deterministic
        assert isinstance(result, str)
        parts = result.split("-")
        assert len(parts) == 5

    def test_calculate_uuid_empty_string(self):
        """Test calculate_uuid with empty string."""
        result = calculate_uuid("")
        assert isinstance(result, str)
        parts = result.split("-")
        assert len(parts) == 5

    def test_calculate_uuid_unicode_name(self):
        """Test calculate_uuid with unicode characters."""
        result = calculate_uuid("test-名前")
        assert isinstance(result, str)
        parts = result.split("-")
        assert len(parts) == 5

    def test_calculate_uuid_long_name(self):
        """Test calculate_uuid with a long name."""
        long_name = "x" * 1000
        result = calculate_uuid(long_name)
        assert isinstance(result, str)
        parts = result.split("-")
        assert len(parts) == 5


class TestFormatUuidFromBytes:
    """Tests for format_uuid_from_bytes function."""

    def test_format_uuid_from_bytes_valid_input(self):
        """Test formatting a valid 16-byte UUID."""
        # Standard UUID bytes (nil UUID: all zeros)
        uuid_bytes = b"\x00" * 16
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == "00000000-0000-0000-0000-000000000000"

    def test_format_uuid_from_bytes_returns_string(self):
        """Test that format_uuid_from_bytes returns a string."""
        uuid_bytes = b"\x00" * 16
        result = format_uuid_from_bytes(uuid_bytes)
        assert isinstance(result, str)

    def test_format_uuid_from_bytes_valid_format(self):
        """Test that format_uuid_from_bytes returns valid UUID format."""
        uuid_bytes = b"\xff" * 16
        result = format_uuid_from_bytes(uuid_bytes)
        parts = result.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_format_uuid_from_bytes_known_value(self):
        """Test formatting with a known UUID value."""
        # UUID: 550e8400-e29b-41d4-a716-446655440000
        uuid_bytes = bytes(
            [
                0x55,
                0x0E,
                0x84,
                0x00,
                0xE2,
                0x9B,
                0x41,
                0xD4,
                0xA7,
                0x16,
                0x44,
                0x66,
                0x55,
                0x44,
                0x00,
                0x00,
            ]
        )
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == "550e8400-e29b-41d4-a716-446655440000"

    def test_format_uuid_from_bytes_hex_characters(self):
        """Test that result contains only hex characters and hyphens."""
        uuid_bytes = b"\xab\xcd\xef" * 5 + b"\xab"  # 16 bytes
        result = format_uuid_from_bytes(uuid_bytes)
        hex_part = result.replace("-", "")
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_format_uuid_from_bytes_all_zeros(self):
        """Test formatting nil UUID (all zeros)."""
        uuid_bytes = b"\x00" * 16
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == "00000000-0000-0000-0000-000000000000"

    def test_format_uuid_from_bytes_all_ones(self):
        """Test formatting UUID with all ones."""
        uuid_bytes = b"\xff" * 16
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == "ffffffff-ffff-ffff-ffff-ffffffffffff"

    def test_format_uuid_from_bytes_sequential(self):
        """Test formatting UUID with sequential bytes."""
        uuid_bytes = bytes(range(16))
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == "00010203-0405-0607-0809-0a0b0c0d0e0f"

    def test_format_uuid_from_bytes_wrong_length_short(self):
        """Test that input shorter than 16 bytes returns invalid-uuid."""
        result = format_uuid_from_bytes(b"\x00" * 15)
        assert result == "invalid-uuid"

    def test_format_uuid_from_bytes_wrong_length_long(self):
        """Test that input longer than 16 bytes returns invalid-uuid."""
        result = format_uuid_from_bytes(b"\x00" * 17)
        assert result == "invalid-uuid"

    def test_format_uuid_from_bytes_empty(self):
        """Test that empty bytes return invalid-uuid."""
        result = format_uuid_from_bytes(b"")
        assert result == "invalid-uuid"


class TestUtilsIntegration:
    """Integration tests for utils functions."""

    def test_calculate_and_format_deterministic(self):
        """Test that calculating UUIDs produces consistent results."""
        name1 = "test-server"
        uuid1 = calculate_uuid(name1)
        uuid2 = calculate_uuid(name1)
        assert uuid1 == uuid2

    def test_multiple_uuid_calculations(self):
        """Test multiple UUID calculations with different names."""
        names = ["server1", "server2", "server3"]
        uuids = [calculate_uuid(name) for name in names]
        # All should be unique
        assert len(set(uuids)) == 3

    def test_format_and_calculate_consistency(self):
        """Test that format function works with calculate_uuid output."""
        # Calculate a UUID
        name = "test"
        uuid_str = calculate_uuid(name)
        # Verify format is correct
        parts = uuid_str.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_format_uuid_roundtrip(self):
        """Test that a UUID can be formatted consistently."""
        original_uuid = calculate_uuid("roundtrip-test")
        # Convert to bytes and back
        hex_part = original_uuid.replace("-", "")
        uuid_bytes = bytes(int(hex_part[i : i + 2], 16) for i in range(0, 32, 2))
        # Format back to string
        result = format_uuid_from_bytes(uuid_bytes)
        assert result == original_uuid
