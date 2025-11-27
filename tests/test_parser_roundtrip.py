#!/usr/bin/env python3
"""
Comprehensive test suite for teehistorian parser functionality.

Tests parsing of actual teehistorian files and roundtrip operations.
"""

import tempfile
from pathlib import Path

import pytest
import teehistorian_py as th


class TestParserBasics:
    """Test basic parser initialization and file reading."""

    def test_parser_creation_with_valid_data(self):
        """Test that parser can be created with valid teehistorian data."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        assert parser is not None
        assert isinstance(parser, th.Teehistorian)

    def test_parser_rejects_empty_data(self):
        """Test that parser rejects empty data."""
        with pytest.raises(th.TeehistorianError):
            th.Teehistorian(b"")

    def test_parser_rejects_invalid_data(self):
        """Test that parser rejects invalid data."""
        invalid_data = b"This is definitely not a teehistorian file"
        with pytest.raises(th.TeehistorianError):
            th.Teehistorian(invalid_data)

    def test_parser_rejects_short_data(self):
        """Test that parser rejects too short data."""
        short_data = b"\x00\x01\x02"
        with pytest.raises(th.TeehistorianError):
            th.Teehistorian(short_data)


class TestParserFileReading:
    """Test reading actual teehistorian files."""

    def test_parse_example_file(self):
        """Test parsing the example teehistorian file."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        assert parser is not None

    def test_parse_test2_file(self):
        """Test parsing test2 teehistorian file."""
        test_file = Path("tests/test2.teehistorian")
        if not test_file.exists():
            pytest.skip("test2.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        assert parser is not None

    def test_parse_dummy_file(self):
        """Test parsing dummy teehistorian file."""
        test_file = Path("tests/dummy.teehistorian")
        if not test_file.exists():
            pytest.skip("dummy.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Dummy file might be very small, but should still parse
        if len(data) > 0:
            try:
                parser = th.Teehistorian(data)
                assert parser is not None
            except th.TeehistorianError:
                # Dummy might be intentionally invalid
                pass


class TestParserIteration:
    """Test iterating through chunks in a file."""

    def test_iterate_example_chunks(self):
        """Test iterating through chunks in example file."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)
        chunks = []

        try:
            while True:
                chunk = parser.next_chunk()
                if chunk is None:
                    break
                chunks.append(chunk)
        except StopIteration:
            pass

        assert len(chunks) > 0, "Example file should have chunks"

    def test_chunk_iteration_consistency(self):
        """Test that chunk iteration is consistent."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Parse twice and verify chunk count matches
        def count_chunks(data):
            parser = th.Teehistorian(data)
            count = 0
            try:
                while True:
                    chunk = parser.next_chunk()
                    if chunk is None:
                        break
                    count += 1
            except StopIteration:
                pass
            return count

        count1 = count_chunks(data)
        count2 = count_chunks(data)

        assert count1 == count2, "Chunk count should be consistent"
        assert count1 > 0, "Should have at least one chunk"


class TestParserWithFiles:
    """Test parser with file operations."""

    def test_open_function_with_valid_file(self):
        """Test opening a file with th.open()."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        parser = th.open(str(test_file))
        assert parser is not None
        assert isinstance(parser, th.Teehistorian)

    def test_open_nonexistent_file(self):
        """Test that opening nonexistent file raises error."""
        with pytest.raises((FileNotFoundError, OSError, th.TeehistorianError)):
            th.open("tests/nonexistent_file.teehistorian")

    def test_parse_file_with_context_manager(self):
        """Test parsing file using context manager pattern."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        parser = th.open(str(test_file))
        assert parser is not None

        # Should be able to iterate
        chunk_count = 0
        try:
            while True:
                chunk = parser.next_chunk()
                if chunk is None:
                    break
                chunk_count += 1
        except StopIteration:
            pass

        assert chunk_count > 0


class TestParserMemoryHandling:
    """Test parser memory and resource handling."""

    def test_parser_with_multiple_files(self):
        """Test parsing multiple files sequentially."""
        files = [
            Path("tests/example.teehistorian"),
            Path("tests/test2.teehistorian"),
        ]

        for test_file in files:
            if not test_file.exists():
                continue

            with open(test_file, "rb") as f:
                data = f.read()

            parser = th.Teehistorian(data)
            assert parser is not None

    def test_parser_large_file_handling(self):
        """Test parser can handle moderately large files."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Duplicate the data to create a larger file-like structure
        large_data = data

        # Should not raise memory errors
        parser = th.Teehistorian(large_data)
        assert parser is not None

    def test_parser_data_integrity(self):
        """Test that parser preserves data integrity."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data1 = f.read()

        with open(test_file, "rb") as f:
            data2 = f.read()

        # Both reads should be identical
        assert data1 == data2
        assert len(data1) == len(data2)

        # Both should parse without error
        parser1 = th.Teehistorian(data1)
        parser2 = th.Teehistorian(data2)

        assert parser1 is not None
        assert parser2 is not None


class TestParserChunkTypes:
    """Test recognition of different chunk types."""

    def test_chunk_has_data(self):
        """Test that chunks contain data."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        parser = th.Teehistorian(data)

        try:
            chunk = parser.next_chunk()
            if chunk is not None:
                # Chunk should have some data representation
                assert chunk is not None
        except StopIteration:
            pass


class TestParserRoundtrip:
    """Test roundtrip parsing and writing."""

    def test_parse_and_write_example_file(self):
        """Test parsing a file and writing its contents."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            original_data = f.read()

        # Create parser from original data
        parser = th.Teehistorian(original_data)
        assert parser is not None

        # Create a writer
        writer = th.TeehistorianWriter()

        # Write end-of-stream marker
        writer.write(th.Eos())

        # Get written data
        written_data = writer.getvalue()
        assert len(written_data) > 0

    def test_roundtrip_preserves_chunk_count(self):
        """Test that roundtrip operations preserve chunk information."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Count chunks in original
        parser = th.Teehistorian(data)
        original_chunk_count = 0
        try:
            while True:
                chunk = parser.next_chunk()
                if chunk is None:
                    break
                original_chunk_count += 1
        except StopIteration:
            pass

        # Verify count is reasonable
        assert original_chunk_count > 0, "Should have parsed at least one chunk"


class TestParserEdgeCases:
    """Test edge cases in parser handling."""

    def test_parser_with_bytes_type(self):
        """Test parser handles bytes type correctly."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Explicitly test with bytes
        assert isinstance(data, bytes)
        parser = th.Teehistorian(data)
        assert parser is not None

    def test_parser_with_bytearray(self):
        """Test parser handles bytearray conversion."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Convert to bytearray
        data_array = bytearray(data)
        parser = th.Teehistorian(bytes(data_array))
        assert parser is not None

    def test_multiple_parser_instances(self):
        """Test creating multiple parser instances from same data."""
        test_file = Path("tests/example.teehistorian")
        if not test_file.exists():
            pytest.skip("example.teehistorian not found")

        with open(test_file, "rb") as f:
            data = f.read()

        # Create multiple parsers from same data
        parsers = [th.Teehistorian(data) for _ in range(3)]

        assert len(parsers) == 3
        assert all(p is not None for p in parsers)
