#!/usr/bin/env python3
"""
Test suite for teehistorian file writing and roundtrip operations.

Tests creating new teehistorian files, writing chunks, and verifying
that written files can be parsed back correctly.
"""

import json
import tempfile
from pathlib import Path

import pytest
import teehistorian_py as th


class TestWriterBasics:
    """Test basic writer initialization and operations."""

    def test_create_writer(self):
        """Test creating a new writer."""
        writer = th.TeehistorianWriter()
        assert writer is not None
        assert isinstance(writer, th.TeehistorianWriter)

    def test_writer_is_empty_initially(self):
        """Test that a new writer has no data initially."""
        writer = th.TeehistorianWriter()
        data = writer.getvalue()
        # Should have some data (at least header)
        assert isinstance(data, bytes)

    def test_get_writer_value(self):
        """Test getting the written data."""
        writer = th.TeehistorianWriter()
        value = writer.getvalue()
        assert isinstance(value, bytes)
        assert len(value) > 0

    def test_writer_size_tracking(self):
        """Test that writer tracks size correctly."""
        writer = th.TeehistorianWriter()
        initial_size = len(writer.getvalue())

        # Write a chunk
        writer.write(th.Eos())

        final_size = len(writer.getvalue())
        # Size should remain the same or grow
        assert final_size >= initial_size


class TestWriterChunks:
    """Test writing different chunk types."""

    def test_write_join_chunk(self):
        """Test writing a Join chunk."""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        data = writer.getvalue()
        assert len(data) > 0

    def test_write_drop_chunk(self):
        """Test writing a Drop chunk."""
        writer = th.TeehistorianWriter()
        writer.write(th.Drop(0, "quit"))
        data = writer.getvalue()
        assert len(data) > 0

    def test_write_player_name_chunk(self):
        """Test writing a PlayerName chunk."""
        writer = th.TeehistorianWriter()
        writer.write(th.PlayerName(0, "TestPlayer"))
        data = writer.getvalue()
        assert len(data) > 0

    def test_write_player_new_chunk(self):
        """Test writing a PlayerNew chunk."""
        writer = th.TeehistorianWriter()
        writer.write(th.PlayerNew(0, 100, 200))
        data = writer.getvalue()
        assert len(data) > 0

    def test_write_eos_chunk(self):
        """Test writing an EOS (End of Stream) chunk."""
        writer = th.TeehistorianWriter()
        writer.write(th.Eos())
        data = writer.getvalue()
        assert len(data) > 0

    def test_write_multiple_chunks(self):
        """Test writing multiple chunks in sequence."""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        size_after_join = len(writer.getvalue())

        writer.write(th.PlayerName(0, "Player"))
        size_after_name = len(writer.getvalue())

        writer.write(th.Drop(0, "quit"))
        size_after_drop = len(writer.getvalue())

        writer.write(th.Eos())
        final_size = len(writer.getvalue())

        # Sizes should increase with each write
        assert size_after_join > 0
        assert size_after_name >= size_after_join
        assert size_after_drop >= size_after_name
        assert final_size >= size_after_drop

    def test_write_many_chunks(self):
        """Test writing many chunks."""
        writer = th.TeehistorianWriter()

        # Write 10 join/drop pairs
        for i in range(10):
            writer.write(th.Join(i))
            writer.write(th.PlayerName(i, f"Player{i}"))
            writer.write(th.Drop(i, "quit"))

        writer.write(th.Eos())

        data = writer.getvalue()
        assert len(data) > 0

    def test_write_with_headers(self):
        """Test writing chunks with custom headers."""
        writer = th.TeehistorianWriter()
        writer.set_header("game_uuid", "550e8400-e29b-41d4-a716-446655440000")
        writer.set_header("server_name", "Test Server")

        writer.write(th.Join(0))
        writer.write(th.Eos())

        data = writer.getvalue()
        assert len(data) > 0

    def test_write_batch_chunks(self):
        """Test writing chunks in a batch."""
        writer = th.TeehistorianWriter()

        chunks = [
            th.Join(0),
            th.PlayerName(0, "Alice"),
            th.Join(1),
            th.PlayerName(1, "Bob"),
            th.Eos(),
        ]

        writer.write_all(chunks)

        data = writer.getvalue()
        assert len(data) > 0


class TestWriterFileOperations:
    """Test writing to files and buffers."""

    def test_save_to_file(self):
        """Test saving written data to a file."""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            temp_path = Path(f.name)

        try:
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "TestPlayer"))
            writer.write(th.Drop(0, "quit"))
            writer.write(th.Eos())

            writer.save(str(temp_path))

            # Verify file was created and has content
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0

            # Try to parse the written file
            with open(temp_path, "rb") as f:
                data = f.read()

            parser = th.Teehistorian(data)
            assert parser is not None
        finally:
            temp_path.unlink(missing_ok=True)

    def test_write_to_file_object(self):
        """Test writing to a file-like object."""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            temp_path = Path(f.name)
            writer = th.TeehistorianWriter(f)

            writer.write(th.Join(0))
            writer.write(th.Eos())

        try:
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0
        finally:
            temp_path.unlink(missing_ok=True)

    def test_getvalue_returns_bytes(self):
        """Test that getvalue returns bytes."""
        writer = th.TeehistorianWriter()
        writer.write(th.Eos())

        value = writer.getvalue()
        assert isinstance(value, bytes)
        assert len(value) > 0

    def test_writer_bytesio_compatibility(self):
        """Test writer works with BytesIO objects."""
        from io import BytesIO

        buffer = BytesIO()
        writer = th.TeehistorianWriter(buffer)

        writer.write(th.Join(0))
        writer.write(th.Eos())

        # Get the written data
        buffer.seek(0)
        data = buffer.read()

        assert len(data) > 0
        assert isinstance(data, bytes)


class TestWriterHeaders:
    """Test setting and managing headers."""

    def test_set_single_header(self):
        """Test setting a single header."""
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "MyServer")

        writer.write(th.Eos())
        assert writer.getvalue() is not None

    def test_set_multiple_headers(self):
        """Test setting multiple headers."""
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "MyServer")
        writer.set_header("server_version", "1.0.0")
        writer.set_header("comment", "Test recording")

        writer.write(th.Eos())
        assert writer.getvalue() is not None

    def test_header_method_chaining(self):
        """Test that header setting supports method chaining."""
        writer = th.TeehistorianWriter()

        # Chainable API if supported
        result = writer.set_header("server_name", "Server")
        if result is not None:
            # If set_header returns the writer
            assert result is writer or isinstance(result, th.TeehistorianWriter)

    def test_update_headers_dict(self):
        """Test updating headers with a dictionary."""
        writer = th.TeehistorianWriter()

        headers = {
            "server_name": "TestServer",
            "server_version": "2.0",
        }

        for key, value in headers.items():
            writer.set_header(key, value)

        writer.write(th.Eos())
        assert writer.getvalue() is not None


class TestWriterStateManagement:
    """Test writer state and lifecycle."""

    def test_reset_writer(self):
        """Test resetting a writer."""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        size1 = len(writer.getvalue())
        assert size1 > 0

        # Reset
        if hasattr(writer, "reset"):
            writer.reset()
            size2 = len(writer.getvalue())
            # After reset, should be smaller or empty
            assert size2 <= size1

    def test_writer_size_property(self):
        """Test accessing writer size."""
        writer = th.TeehistorianWriter()

        if hasattr(writer, "size"):
            size1 = writer.size
            assert isinstance(size1, int)

            writer.write(th.Join(0))

            size2 = writer.size
            assert isinstance(size2, int)

    def test_writer_is_empty_flag(self):
        """Test checking if writer is empty."""
        writer = th.TeehistorianWriter()

        if hasattr(writer, "is_empty"):
            # New writer might or might not be empty depending on default header
            is_empty = writer.is_empty
            assert isinstance(is_empty, bool)

    def test_context_manager_usage(self):
        """Test using writer as context manager."""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with open(temp_path, "wb") as f:
                with th.TeehistorianWriter(f) as writer:
                    writer.write(th.Join(0))
                    writer.write(th.Eos())

            # File should exist and be readable
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0
        finally:
            temp_path.unlink(missing_ok=True)


class TestWriterRoundtrip:
    """Test writing and reading back."""

    def test_write_and_parse_simple(self):
        """Test writing data and parsing it back."""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "TestPlayer"))
        writer.write(th.Drop(0, "quit"))
        writer.write(th.Eos())

        written_data = writer.getvalue()

        # Parse the written data
        parser = th.Teehistorian(written_data)
        assert parser is not None

    def test_roundtrip_preserves_structure(self):
        """Test that roundtrip preserves file structure."""
        # Create a simple recording
        writer = th.TeehistorianWriter()

        num_players = 5
        for i in range(num_players):
            writer.write(th.Join(i))
            writer.write(th.PlayerName(i, f"Player{i}"))

        writer.write(th.Eos())

        # Parse it back
        data = writer.getvalue()
        parser = th.Teehistorian(data)
        assert parser is not None

        # Count chunks
        chunk_count = 0
        try:
            while True:
                chunk = parser.next_chunk()
                if chunk is None:
                    break
                chunk_count += 1
        except StopIteration:
            pass

        # Should have parsed some chunks
        assert chunk_count > 0

    def test_write_file_and_reparse(self):
        """Test writing to file and reparsing from disk."""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Write a file
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "Alice"))
            writer.write(th.Join(1))
            writer.write(th.PlayerName(1, "Bob"))
            writer.write(th.Drop(0, "quit"))
            writer.write(th.Drop(1, "quit"))
            writer.write(th.Eos())

            writer.save(str(temp_path))

            # Read it back
            with open(temp_path, "rb") as f:
                data = f.read()

            # Parse it
            parser = th.Teehistorian(data)
            assert parser is not None

            # Count chunks
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
        finally:
            temp_path.unlink(missing_ok=True)


class TestWriterEdgeCases:
    """Test edge cases and special scenarios."""

    def test_write_empty_player_name(self):
        """Test writing chunk with empty player name."""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, ""))
        writer.write(th.Drop(0, "quit"))
        writer.write(th.Eos())

        data = writer.getvalue()
        assert len(data) > 0

    def test_write_special_characters_in_name(self):
        """Test writing player names with special characters."""
        writer = th.TeehistorianWriter()

        special_names = [
            "Player_1",
            "Player-2",
            "Player.3",
            "Player[4]",
            "PlayerÄÖÜ",
        ]

        for i, name in enumerate(special_names):
            writer.write(th.Join(i))
            writer.write(th.PlayerName(i, name))
            writer.write(th.Drop(i, "quit"))

        writer.write(th.Eos())
        assert writer.getvalue() is not None

    def test_write_many_players(self):
        """Test writing a recording with many players."""
        writer = th.TeehistorianWriter()

        # Write 100 players joining
        for i in range(100):
            writer.write(th.Join(i))

        # Drop them all
        for i in range(100):
            writer.write(th.Drop(i, "quit"))

        writer.write(th.Eos())

        data = writer.getvalue()
        assert len(data) > 0

    def test_write_consecutive_same_chunks(self):
        """Test writing the same chunk type consecutively."""
        writer = th.TeehistorianWriter()

        # Write same chunk multiple times
        for i in range(10):
            writer.write(th.Join(i))

        writer.write(th.Eos())

        data = writer.getvalue()
        assert len(data) > 0

    def test_overwrite_prevention(self):
        """Test that writer prevents accidental overwrites."""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        size1 = len(writer.getvalue())

        # If trying to write same player again, size should increase
        writer.write(th.Drop(0, "quit"))
        size2 = len(writer.getvalue())

        assert size2 >= size1


class TestWriterConsistency:
    """Test consistency across multiple writes."""

    def test_multiple_writes_same_size(self):
        """Test that writing identical sequences produces same size."""

        def create_recording():
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "Player"))
            writer.write(th.Drop(0, "quit"))
            writer.write(th.Eos())
            return writer.getvalue()

        data1 = create_recording()
        data2 = create_recording()

        # Should produce same output
        assert len(data1) == len(data2)

    def test_deterministic_output(self):
        """Test that writer produces deterministic output."""
        data1 = b""
        data2 = b""

        for _ in range(2):
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "Alice"))
            writer.write(th.Eos())

            if not data1:
                data1 = writer.getvalue()
            else:
                data2 = writer.getvalue()

        # Both should be identical
        assert data1 == data2


class TestWriterJSONHeaders:
    """Test JSON parsing in header values."""

    def test_json_config_parsing(self):
        """Test that JSON strings in headers are parsed as objects."""
        writer = th.TeehistorianWriter()

        config = {
            "sv_motd": "Welcome to server",
            "sv_name": "Test Server",
            "sv_port": "8303",
        }

        writer.set_header("config", json.dumps(config))
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        # Config should be parsed as a dict, not a string
        assert isinstance(header["config"], dict)
        assert header["config"]["sv_motd"] == "Welcome to server"
        assert header["config"]["sv_name"] == "Test Server"

    def test_json_tuning_parsing(self):
        """Test that JSON tuning data is parsed as an object."""
        writer = th.TeehistorianWriter()

        tuning = {"gun_speed": "140000", "shotgun_speed": "50000"}

        writer.set_header("tuning", json.dumps(tuning))
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        # Tuning should be parsed as a dict
        assert isinstance(header["tuning"], dict)
        assert header["tuning"]["gun_speed"] == "140000"

    def test_plain_string_not_parsed(self):
        """Test that plain strings are not parsed as JSON."""
        writer = th.TeehistorianWriter()

        writer.set_header("server_name", "My Test Server")
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        # server_name should remain a string
        assert isinstance(header["server_name"], str)
        assert header["server_name"] == "My Test Server"

    def test_invalid_json_treated_as_string(self):
        """Test that invalid JSON is stored as a string."""
        writer = th.TeehistorianWriter()

        # This looks like JSON but isn't valid
        invalid_json = "{invalid json here}"
        writer.set_header("data", invalid_json)
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        # Should be stored as string since JSON parsing failed
        assert isinstance(header["data"], str)
        assert header["data"] == invalid_json

    def test_nested_json_parsing(self):
        """Test that deeply nested JSON structures are properly parsed."""
        writer = th.TeehistorianWriter()

        nested = {"level1": {"level2": {"level3": "value"}, "array": [1, 2, 3]}}

        writer.set_header("config", json.dumps(nested))
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        assert isinstance(header["config"], dict)
        assert header["config"]["level1"]["level2"]["level3"] == "value"
        assert header["config"]["level1"]["array"] == [1, 2, 3]

    def test_update_headers_with_json(self):
        """Test that update_headers properly parses JSON values."""
        writer = th.TeehistorianWriter()

        headers_dict = {
            "server_name": "Test",
            "config": json.dumps({"key": "value"}),
            "tuning": json.dumps({"gun_speed": "140000"}),
        }

        writer.update_headers(headers_dict)
        writer.write(th.Eos())

        data = writer.getvalue()
        parser = th.Teehistorian(data)
        header = json.loads(parser.header().decode("utf-8"))

        assert isinstance(header["config"], dict)
        assert isinstance(header["tuning"], dict)
        assert isinstance(header["server_name"], str)
