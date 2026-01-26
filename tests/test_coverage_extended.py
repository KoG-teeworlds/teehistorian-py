#!/usr/bin/env python3
"""Extended coverage tests for teehistorian_py module"""

import json
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
import teehistorian_py as th


class TestTeehistorianWriterAdvanced:
    """Advanced tests for TeehistorianWriter to improve coverage"""

    def test_writer_with_file_object(self):
        """Test writing to a file-like object"""
        buffer = BytesIO()
        writer = th.TeehistorianWriter(file=buffer)
        writer.write(th.Join(0))
        writer.write(th.Eos())
        writer.__exit__(None, None, None)

        assert buffer.tell() > 0
        buffer.seek(0)
        data = buffer.read()
        assert len(data) > 0

    def test_writer_reset(self):
        """Test resetting a writer"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        size_before_reset = writer.size
        assert size_before_reset > 0

        writer.reset()
        assert writer.size == 0
        assert writer.is_empty
        assert not writer._closed

    def test_writer_is_empty_property(self):
        """Test is_empty property"""
        writer = th.TeehistorianWriter()
        assert writer.is_empty

        writer.write(th.Join(0))
        assert not writer.is_empty

    def test_writer_size_property(self):
        """Test size property"""
        writer = th.TeehistorianWriter()
        initial_size = writer.size
        assert initial_size == 0

        writer.write(th.Join(0))
        assert writer.size > initial_size

    def test_writer_repr(self):
        """Test __repr__ method"""
        writer = th.TeehistorianWriter()
        repr_str = repr(writer)
        assert "TeehistorianWriter" in repr_str
        assert "size=" in repr_str
        assert "empty" in repr_str

    def test_writer_closed_error_on_write(self):
        """Test that writing to closed writer raises error"""
        writer = th.TeehistorianWriter()
        writer._closed = True

        with pytest.raises(ValueError, match="closed"):
            writer.write(th.Join(0))

    def test_writer_closed_error_on_header(self):
        """Test that setting header on closed writer raises error"""
        writer = th.TeehistorianWriter()
        writer._closed = True

        with pytest.raises(ValueError, match="closed"):
            writer.set_header("key", "value")

    def test_writer_context_manager_with_exception(self):
        """Test context manager behavior when exception occurs"""
        buffer = BytesIO()
        try:
            with th.TeehistorianWriter(file=buffer) as writer:
                writer.write(th.Join(0))
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        # Should still have written data
        assert buffer.tell() > 0 or writer.size > 0

    def test_writer_write_all(self):
        """Test write_all method"""
        writer = th.TeehistorianWriter()
        chunks = [
            th.Join(0),
            th.PlayerName(0, "Player1"),
            th.Join(1),
            th.PlayerName(1, "Player2"),
        ]

        writer.write_all(chunks)
        assert writer.size > 0

    def test_writer_method_chaining(self):
        """Test method chaining"""
        writer = (
            th.TeehistorianWriter()
            .set_header("key1", "val1")
            .set_header("key2", "val2")
            .write(th.Join(0))
            .write(th.PlayerName(0, "Test"))
        )

        assert writer.get_header("key1") == "val1"
        assert writer.get_header("key2") == "val2"
        assert writer.size > 0

    def test_writer_getvalue(self):
        """Test getvalue method"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Eos())

        data = writer.getvalue()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_writer_writeto_method(self):
        """Test writeto method"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Eos())

        buffer = BytesIO()
        writer.writeto(buffer)

        assert buffer.tell() > 0

    def test_writer_save_to_path(self):
        """Test save method with Path object"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.teehistorian"

            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            assert filepath.exists()
            assert filepath.stat().st_size > 0


class TestParsingAdvanced:
    """Advanced parsing tests"""

    def test_parse_from_path_string(self):
        """Test parsing from string path"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            # Create a file
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            # Parse from string path
            parser = th.parse(filepath)
            chunks = list(parser)
            assert len(chunks) >= 2
        finally:
            Path(filepath).unlink()

    def test_parse_from_path_object(self):
        """Test parsing from Path object"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = Path(f.name)

        try:
            # Create a file
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            # Parse from Path object
            parser = th.parse(filepath)
            chunks = list(parser)
            assert len(chunks) >= 2
        finally:
            filepath.unlink()

    def test_open_function(self):
        """Test open function (alias for parse)"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            parser = th.open(filepath)
            chunks = list(parser)
            assert len(chunks) >= 2
        finally:
            Path(filepath).unlink()

    def test_parser_context_manager(self):
        """Test parser as context manager"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            writer = th.TeehistorianWriter()
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            with th.open(filepath) as parser:
                chunks = list(parser)
                assert len(chunks) >= 2
        finally:
            Path(filepath).unlink()

    def test_parser_get_header_str(self):
        """Test getting header as string"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            writer = th.TeehistorianWriter()
            writer.set_header("test_key", "test_value")
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            parser = th.Teehistorian(Path(filepath).read_bytes())
            header_str = parser.get_header_str()

            assert isinstance(header_str, str)
            header_json = json.loads(header_str)
            assert header_json.get("test_key") == "test_value"
        finally:
            Path(filepath).unlink()


class TestCreateFunction:
    """Tests for the create() convenience function"""

    def test_create_with_no_headers(self):
        """Test create() with no headers"""
        writer = th.create()
        assert isinstance(writer, th.TeehistorianWriter)
        assert not writer._closed

    def test_create_with_headers(self):
        """Test create() with headers"""
        writer = th.create(server_name="Test Server", map="dm6", comment="Test run")

        assert writer.get_header("server_name") == "Test Server"
        assert writer.get_header("map") == "dm6"
        assert writer.get_header("comment") == "Test run"

    def test_create_and_use_context_manager(self):
        """Test create() with context manager"""
        with th.create(server_name="Test") as writer:
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "TestPlayer"))
            # EOS should be auto-written on exit

        # Verify we have data
        data = writer.getvalue()
        assert len(data) > 0


class TestChunkTypes:
    """Tests for various chunk types"""

    def test_write_and_read_all_chunk_types(self):
        """Test writing and reading various chunk types"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            writer = th.TeehistorianWriter()

            # Write various chunks
            writer.write(th.Join(0))
            writer.write(th.PlayerName(0, "TestPlayer"))
            writer.write(th.PlayerTeam(0, 1))
            writer.write(th.PlayerReady(0))
            writer.write(th.InputNew(0, b"\x00\x01"))
            writer.write(th.InputDiff(0, b"\x01"))
            writer.write(th.TickSkip(5))
            writer.write(th.Eos())

            writer.save(filepath)

            # Read back
            parser = th.Teehistorian(Path(filepath).read_bytes())
            chunks = list(parser)

            # Should have at least the chunks we wrote
            assert len(chunks) >= 8

            # Check types
            assert isinstance(chunks[0], th.Join)
            assert isinstance(chunks[-1], th.Eos)
        finally:
            Path(filepath).unlink()

    def test_net_message_with_bytes(self):
        """Test NetMessage with bytes"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.NetMessage(0, b"Hello World"))
        writer.write(th.Eos())

        assert writer.size > 0

    def test_console_command(self):
        """Test ConsoleCommand chunk"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.ConsoleCommand(0, 1, "say", ["hello", "world"]))
        writer.write(th.Eos())

        assert writer.size > 0

    def test_drop_chunk(self):
        """Test Drop chunk"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Drop(0, "quit"))
        writer.write(th.Eos())

        assert writer.size > 0

    def test_player_diff_chunk(self):
        """Test PlayerDiff chunk"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.PlayerDiff(0, 1, 2))
        writer.write(th.Eos())

        assert writer.size > 0

    def test_auth_login_chunk(self):
        """Test AuthLogin chunk"""
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.AuthLogin(0, 1, "player123"))
        writer.write(th.Eos())

        assert writer.size > 0

    def test_ddnet_version_chunk(self):
        """Test DdnetVersion chunk - requires complex initialization"""
        # DdnetVersion requires special initialization from parsing
        # This is a placeholder test that verifies it's exported
        writer = th.TeehistorianWriter()
        writer.write(th.Join(0))
        writer.write(th.Eos())

        assert writer.size > 0
        # Verify DdnetVersion is available in module
        assert hasattr(th, "DdnetVersion")


class TestExceptionHandling:
    """Tests for exception handling"""

    def test_version_attribute(self):
        """Test __version__ attribute"""
        assert hasattr(th, "__version__")
        assert isinstance(th.__version__, str)
        assert len(th.__version__) > 0

    def test_all_exports(self):
        """Test that all items in __all__ are exported"""
        for name in th.__all__:
            assert hasattr(th, name), f"Missing export: {name}"

    def test_exception_hierarchy(self):
        """Test exception class hierarchy"""
        assert issubclass(th.ParseError, th.TeehistorianError)
        assert issubclass(th.ValidationError, th.TeehistorianError)
        assert issubclass(th.FileError, th.TeehistorianError)
        assert issubclass(th.WriteError, th.TeehistorianError)


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_calculate_uuid(self):
        """Test UUID calculation"""
        uuid1 = th.calculate_uuid("test_chunk")
        uuid2 = th.calculate_uuid("test_chunk")

        # Same inputs should produce same UUID
        assert uuid1 == uuid2
        assert isinstance(uuid1, str)
        assert "-" in uuid1  # UUID format includes hyphens

    def test_format_uuid_from_bytes(self):
        """Test UUID formatting from bytes"""
        test_bytes = b"\x12\x34\x56\x78" * 4  # 16 bytes
        uuid_str = th.format_uuid_from_bytes(test_bytes)

        assert isinstance(uuid_str, str)
        assert len(uuid_str) > 0
        # Should contain hyphens in standard UUID format
        assert "-" in uuid_str or len(uuid_str) == 32


class TestHeaderOperations:
    """Tests for header operations"""

    def test_set_get_multiple_headers(self):
        """Test setting and getting multiple headers"""
        writer = th.TeehistorianWriter()

        headers = {
            "server_name": "TestServer",
            "map": "dm6",
            "timestamp": "2024-01-01",
            "comment": "Test file",
            "version": "1.0",
        }

        for key, value in headers.items():
            writer.set_header(key, value)

        for key, value in headers.items():
            assert writer.get_header(key) == value

    def test_update_headers_overwrites(self):
        """Test that update_headers overwrites existing headers"""
        writer = th.TeehistorianWriter()

        writer.set_header("key1", "old_value")
        writer.update_headers({"key1": "new_value"})

        assert writer.get_header("key1") == "new_value"

    def test_header_preservation_in_file(self):
        """Test that headers are preserved when saved and loaded"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            headers_to_set = {
                "custom_header_1": "value1",
                "custom_header_2": "value2",
                "custom_header_3": "value3",
            }

            # Write with headers
            writer = th.TeehistorianWriter()
            writer.update_headers(headers_to_set)
            writer.write(th.Join(0))
            writer.write(th.Eos())
            writer.save(filepath)

            # Read back
            parser = th.Teehistorian(Path(filepath).read_bytes())
            header_str = parser.get_header_str()
            header_json = json.loads(header_str)

            for key, value in headers_to_set.items():
                assert header_json.get(key) == value
        finally:
            Path(filepath).unlink()


class TestComplexScenarios:
    """Tests for complex real-world scenarios"""

    def test_large_file_with_many_players(self):
        """Test creating a file with many players"""
        writer = th.TeehistorianWriter()
        writer.set_header("server_name", "Large Test")

        # Add 50 players
        for i in range(50):
            writer.write(th.Join(i))
            writer.write(th.PlayerName(i, f"Player_{i}"))
            writer.write(th.PlayerTeam(i, i % 2))
            writer.write(th.PlayerReady(i))

        writer.write(th.Eos())

        assert writer.size > 0

    def test_roundtrip_with_complex_chunks(self):
        """Test writing and reading back complex chunk sequence"""
        with tempfile.NamedTemporaryFile(suffix=".teehistorian", delete=False) as f:
            filepath = f.name

        try:
            # Write complex sequence
            writer = th.TeehistorianWriter()
            writer.set_header("test", "value")

            for i in range(10):
                writer.write(th.Join(i))
                writer.write(th.PlayerName(i, f"P{i}"))
                writer.write(th.InputNew(i, b"\x00"))
                writer.write(th.InputDiff(i, b"\x01"))
                writer.write(th.PlayerDiff(i, 1, 2))

            writer.write(th.TickSkip(10))
            writer.write(th.Eos())
            writer.save(filepath)

            # Read back - must access header before iterating chunks
            data = Path(filepath).read_bytes()
            parser = th.Teehistorian(data)

            # Get header BEFORE iterating chunks
            header = json.loads(parser.get_header_str())
            assert header.get("test") == "value"

            chunks = list(parser)
            assert len(chunks) > 50  # Should have many chunks
        finally:
            Path(filepath).unlink()

    def test_alternating_writes_and_saves(self):
        """Test alternating between writes and saves"""
        writer = th.TeehistorianWriter()

        writer.write(th.Join(0))
        data1 = writer.getvalue()

        writer.write(th.PlayerName(0, "Test"))
        data2 = writer.getvalue()

        assert len(data2) > len(data1)

        writer.write(th.Eos())
        data3 = writer.getvalue()

        assert len(data3) > len(data2)
