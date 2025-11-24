#!/usr/bin/env python3
"""
Comprehensive test suite for teehistorian_py module.

Uses pytest conventions and best practices for clear, maintainable tests.
"""

import tempfile
from pathlib import Path

try:
    import pytest
except ImportError:
    # Fallback for running without pytest
    import unittest as pytest

import teehistorian_py as th

# ============================================================================
# Module and Import Tests
# ============================================================================


class TestModuleImports:
    """Test that all expected classes and functions are properly exported."""

    def test_core_classes_exported(self):
        """Test core parsing and writing classes are available."""
        assert hasattr(th, "Teehistorian")
        assert hasattr(th, "TeehistorianParser")
        assert hasattr(th, "TeehistorianWriter")
        assert hasattr(th, "TeehistorianError")

    def test_chunk_types_exported(self):
        """Test all chunk types are available."""
        chunk_types = [
            "Join",
            "JoinVer6",
            "Drop",
            "PlayerReady",
            "PlayerNew",
            "PlayerOld",
            "PlayerTeam",
            "PlayerName",
            "PlayerDiff",
            "InputNew",
            "InputDiff",
            "NetMessage",
            "ConsoleCommand",
            "AuthLogin",
            "DdnetVersion",
            "TickSkip",
            "TeamLoadSuccess",
            "TeamLoadFailure",
            "AntiBot",
            "Eos",
            "Unknown",
            "CustomChunk",
            "Generic",
        ]
        for chunk_type in chunk_types:
            assert hasattr(th, chunk_type), f"Missing chunk type: {chunk_type}"

    def test_utility_functions_exported(self):
        """Test utility functions are available."""
        assert hasattr(th, "parse")
        assert hasattr(th, "open")
        assert hasattr(th, "create")
        assert hasattr(th, "calculate_uuid")
        assert hasattr(th, "format_uuid_from_bytes")

    def test_exception_types_exported(self):
        """Test exception types are available."""
        assert hasattr(th, "ParseError")
        assert hasattr(th, "ValidationError")
        assert hasattr(th, "FileError")
        assert hasattr(th, "WriteError")


# ============================================================================
# Chunk Creation Tests
# ============================================================================


class TestChunkCreation:
    """Test creating and validating chunk objects."""

    def test_join_chunk(self):
        """Test Join chunk creation and properties."""
        join = th.Join(42)
        assert join.client_id == 42
        assert "Join" in repr(join)

    def test_drop_chunk(self):
        """Test Drop chunk creation with reason."""
        drop = th.Drop(1, "timeout")
        assert drop.client_id == 1
        assert drop.reason == "timeout"

    def test_player_new_chunk(self):
        """Test PlayerNew chunk with position."""
        player = th.PlayerNew(5, 100, 200)
        assert player.client_id == 5
        assert player.x == 100
        assert player.y == 200

    def test_player_diff_chunk(self):
        """Test PlayerDiff chunk for position updates."""
        diff = th.PlayerDiff(3, 10, -5)
        assert diff.client_id == 3
        assert diff.dx == 10
        assert diff.dy == -5

    def test_tick_skip_chunk(self):
        """Test TickSkip chunk for time advancement."""
        skip = th.TickSkip(120)
        assert skip.dt == 120

    def test_eos_chunk(self):
        """Test End of Stream chunk."""
        eos = th.Eos()
        assert eos is not None
        assert "Eos" in repr(eos)


# ============================================================================
# Parser Tests
# ============================================================================


class TestParser:
    """Test teehistorian file parsing."""

    def test_parser_rejects_empty_data(self):
        """Test that parser rejects empty data."""
        with pytest.raises((th.TeehistorianError, th.ValidationError)):
            th.Teehistorian(b"")

    def test_parser_rejects_invalid_data(self):
        """Test that parser rejects obviously invalid data."""
        with pytest.raises((th.TeehistorianError, th.ValidationError)):
            th.Teehistorian(b"\x00" * 32)

    def test_parser_rejects_short_data(self):
        """Test that parser rejects data that's too short."""
        with pytest.raises((th.TeehistorianError, th.ValidationError)):
            th.Teehistorian(b"short")

    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            th.parse("nonexistent_file_xyz.teehistorian")

    def test_open_function_exists(self):
        """Test that open() is available as alias for parse()."""
        assert callable(th.open)
        assert th.open is not None

    def test_open_nonexistent_file(self):
        """Test opening a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            th.open("nonexistent_file_xyz.teehistorian")


# ============================================================================
# Exception Tests
# ============================================================================


class TestExceptions:
    """Test exception hierarchy and functionality."""

    def test_teehistorian_error_base(self):
        """Test TeehistorianError is proper exception."""
        assert issubclass(th.TeehistorianError, Exception)
        error = th.TeehistorianError("test message")
        assert str(error) == "test message"

    def test_error_hierarchy(self):
        """Test error classes inherit correctly."""
        assert issubclass(th.ParseError, th.TeehistorianError)
        assert issubclass(th.ValidationError, th.TeehistorianError)
        assert issubclass(th.FileError, th.TeehistorianError)
        assert issubclass(th.WriteError, th.TeehistorianError)

    def test_error_instantiation(self):
        """Test creating all error types."""
        errors = [
            th.TeehistorianError("base"),
            th.ParseError("parse"),
            th.ValidationError("validation"),
            th.FileError("file"),
            th.WriteError("write"),
        ]
        for error in errors:
            assert isinstance(error, Exception)
            assert len(str(error)) > 0

    def test_error_raising_and_catching(self):
        """Test raising and catching custom exceptions."""
        with pytest.raises(th.ValidationError):
            raise th.ValidationError("test validation error")

        with pytest.raises(th.TeehistorianError):
            raise th.ParseError("test parse error")


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions for UUID calculation and formatting."""

    def test_calculate_uuid_valid_format(self):
        """Test UUID calculation produces valid format."""
        name = "kog-one-login@kog.tw"
        uuid = th.calculate_uuid(name)
        assert len(uuid) == 36
        assert uuid.count("-") == 4
        assert uuid != "invalid-uuid"

    def test_calculate_uuid_different_inputs(self):
        """Test that different inputs produce different UUIDs."""
        uuid1 = th.calculate_uuid("user1@example.com")
        uuid2 = th.calculate_uuid("user2@example.com")
        assert uuid1 != uuid2

    def test_calculate_uuid_empty_string(self):
        """Test UUID calculation with empty string."""
        uuid = th.calculate_uuid("")
        # Empty string should produce a valid UUID format
        assert len(uuid) == 36
        assert uuid.count("-") == 4

    def test_format_uuid_from_bytes_valid(self):
        """Test formatting valid UUID bytes."""
        uuid_bytes = b"\xa1\xb2\xc3\xd4\xe5\xf6\x37\x89\x8a\xbc\xde\xf0\x12\x34\x56\x78"
        uuid = th.format_uuid_from_bytes(uuid_bytes)
        assert len(uuid) == 36
        assert uuid.count("-") == 4
        assert uuid == "a1b2c3d4-e5f6-3789-8abc-def012345678"

    def test_format_uuid_from_bytes_invalid_length_short(self):
        """Test formatting with too few bytes."""
        uuid = th.format_uuid_from_bytes(b"\x00" * 15)
        assert uuid == "invalid-uuid"

    def test_format_uuid_from_bytes_invalid_length_long(self):
        """Test formatting with too many bytes."""
        uuid = th.format_uuid_from_bytes(b"\x00" * 17)
        assert uuid == "invalid-uuid"

    def test_format_uuid_from_bytes_empty(self):
        """Test formatting with empty bytes."""
        uuid = th.format_uuid_from_bytes(b"")
        assert uuid == "invalid-uuid"

    def test_format_uuid_from_bytes_invalid_type(self):
        """Test formatting with invalid input type."""
        try:
            result = th.format_uuid_from_bytes("not bytes")
            # Either returns "invalid-uuid" or raises an exception is acceptable
            assert result == "invalid-uuid"
        except (TypeError, AttributeError):
            # Exception is also acceptable
            pass


# ============================================================================
# Writer Creation Tests
# ============================================================================


class TestWriterCreation:
    """Test creating and initializing writers."""

    def test_create_writer(self):
        """Test creating a new writer instance."""
        writer = th.create()
        assert isinstance(writer, th.TeehistorianWriter)

    def test_create_writer_empty(self):
        """Test new writer starts empty."""
        writer = th.create()
        assert writer.size() == 0
        assert writer.is_empty()

    def test_create_writer_with_headers(self):
        """Test creating writer with initial headers."""
        writer = th.create(server_name="Test Server", comment="Test comment")
        assert writer.size() == 0  # Headers don't count until written
        assert writer.is_empty()

    def test_writer_repr(self):
        """Test writer string representation."""
        writer = th.create()
        repr_str = repr(writer)
        assert "TeehistorianWriter" in repr_str
        assert "size=" in repr_str


# ============================================================================
# Writer Header Tests
# ============================================================================


class TestWriterHeaders:
    """Test writer header manipulation."""

    def test_set_header(self):
        """Test setting individual header fields."""
        writer = th.create()
        result = writer.set_header("test_field", "test_value")
        # set_header returns self for method chaining
        assert result is writer

    def test_set_multiple_headers(self):
        """Test setting multiple headers."""
        writer = th.create()
        writer.set_header("field1", "value1")
        writer.set_header("field2", "value2")
        writer.set_header("server_name", "My Server")
        # Just verify no errors occurred
        assert writer is not None

    def test_update_headers_dict(self):
        """Test updating headers from dictionary."""
        writer = th.create()
        headers = {
            "server_name": "Test Server",
            "comment": "Test comment",
            "map_name": "Test Map",
        }
        result = writer.update_headers(headers)
        # update_headers returns self for method chaining
        assert result is writer

    def test_header_method_chaining(self):
        """Test that header methods support chaining."""
        writer = (
            th.create()
            .set_header("server_name", "Server")
            .set_header("comment", "Comment")
            .update_headers({"map_name": "Map"})
        )
        assert isinstance(writer, th.TeehistorianWriter)


# ============================================================================
# Writer Chunk Writing Tests
# ============================================================================


class TestWriterChunks:
    """Test writing various chunk types."""

    def test_write_single_chunk(self):
        """Test writing a single chunk."""
        writer = th.create()
        result = writer.write(th.Join(0))
        assert result is writer
        assert writer.size() > 0

    def test_write_join_chunks(self):
        """Test writing player join chunks."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.JoinVer6(1))
        assert writer.size() > 0
        assert not writer.is_empty()

    def test_write_player_chunks(self):
        """Test writing player-related chunks."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.PlayerReady(0))
        writer.write(th.PlayerNew(0, 100, 200))
        writer.write(th.PlayerName(0, "TestPlayer"))
        writer.write(th.PlayerTeam(0, 1))
        writer.write(th.PlayerDiff(0, 5, -3))
        writer.write(th.PlayerOld(0))
        writer.write(th.Drop(0, "quit"))
        assert writer.size() > 0

    def test_write_server_chunks(self):
        """Test writing server event chunks."""
        writer = th.create()
        writer.write(th.TickSkip(60))
        writer.write(
            th.TeamLoadSuccess(
                1, "550e8400-e29b-41d4-a716-446655440000", "team_save_data"
            )
        )
        writer.write(th.TeamLoadFailure(2))
        writer.write(th.AntiBot("detection_event"))
        assert writer.size() > 0

    def test_write_communication_chunks(self):
        """Test writing communication chunks."""
        writer = th.create()
        writer.write(th.NetMessage(0, "Hello World"))
        writer.write(th.ConsoleCommand(0, 1, "say", "test message"))
        assert writer.size() > 0

    def test_write_eos_chunk(self):
        """Test writing End of Stream chunk."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.Eos())
        assert writer.size() > 0

    def test_write_multiple_chunks_chaining(self):
        """Test writing multiple chunks with method chaining."""
        writer = (
            th.create()
            .write(th.Join(0))
            .write(th.PlayerName(0, "Player"))
            .write(th.PlayerNew(0, 100, 200))
            .write(th.Eos())
        )
        assert writer.size() > 0

    def test_write_all_batch(self):
        """Test writing multiple chunks in batch."""
        writer = th.create()
        chunks = [
            th.Join(10),
            th.PlayerName(10, "BatchPlayer"),
            th.PlayerNew(10, 300, 400),
            th.TickSkip(60),
            th.Eos(),
        ]
        result = writer.write_all(chunks)
        assert result is writer
        assert writer.size() > 0


# ============================================================================
# Writer File Operations Tests
# ============================================================================


class TestWriterFileOperations:
    """Test saving and exporting writer data."""

    def test_getvalue_returns_bytes(self):
        """Test getvalue() returns bytes."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.Eos())
        data = writer.getvalue()
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_save_to_file(self):
        """Test saving writer to file path."""
        writer = th.create()
        writer.set_header("server_name", "Save Test")
        writer.write(th.Join(42))
        writer.write(th.PlayerName(42, "SavePlayer"))
        writer.write(th.Eos())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".teehistorian") as f:
            tmp_path = f.name

        try:
            writer.save(tmp_path)
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_writeto_file_object(self):
        """Test writing to file-like object."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.Eos())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".teehistorian") as f:
            tmp_path = f.name

        try:
            with open(tmp_path, "wb") as f:
                writer.writeto(f)
            assert Path(tmp_path).stat().st_size > 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_getvalue_bytes_roundtrip(self):
        """Test saving and loading bytes."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.Eos())

        data = writer.getvalue()
        assert isinstance(data, bytes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".teehistorian") as f:
            tmp_path = f.name

        try:
            Path(tmp_path).write_bytes(data)
            assert Path(tmp_path).stat().st_size > 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)


# ============================================================================
# Writer State Management Tests
# ============================================================================


class TestWriterStateManagement:
    """Test writer state and reset functionality."""

    def test_size_increases_with_writes(self):
        """Test that size increases as chunks are written."""
        writer = th.create()
        initial_size = writer.size()
        writer.write(th.Join(0))
        after_write = writer.size()
        assert after_write > initial_size, "Size should increase after writing chunks"

    def test_is_empty_flag(self):
        """Test is_empty() flag."""
        writer = th.create()
        assert writer.is_empty()
        writer.write(th.Join(0))
        assert not writer.is_empty()

    def test_reset_clears_data(self):
        """Test reset() clears all data."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player"))
        assert writer.size() > 0
        assert not writer.is_empty()

        writer.reset()
        assert writer.size() == 0
        assert writer.is_empty()

    def test_reset_allows_reuse(self):
        """Test writer can be reused after reset."""
        writer = th.create()
        writer.write(th.Join(0))
        _ = writer.size()  # Store first size (not used in assertion)

        writer.reset()
        assert writer.is_empty()

        writer.write(th.Join(1))
        writer.write(th.PlayerName(1, "Player2"))
        assert writer.size() > 0


# ============================================================================
# Writer Context Manager Tests
# ============================================================================


class TestWriterContextManager:
    """Test writer as context manager."""

    def test_context_manager_basic(self):
        """Test basic context manager usage."""
        with th.create() as writer:
            writer.write(th.Join(0))
            writer.write(th.Eos())
            assert writer.size() > 0

    def test_context_manager_with_headers(self):
        """Test context manager with header setup."""
        with th.create() as writer:
            writer.set_header("server_name", "Context Test")
            writer.write(th.Join(99))
            writer.write(th.PlayerName(99, "ContextPlayer"))

    def test_context_manager_auto_eos(self):
        """Test that context manager handles cleanup."""
        with th.create() as writer:
            writer.set_header("server_name", "Test")
            writer.write(th.Join(0))
            size_in_context = writer.size()

        # Writer should be in closed state after exiting
        assert size_in_context > 0

    def test_context_manager_method_chaining(self):
        """Test method chaining with context manager."""
        with (
            th.create()
            .set_header("server_name", "Chaining Test")
            .write(th.Join(42))
            .write(th.PlayerName(42, "ChainTest"))
            .write(th.Eos())
        ) as writer:
            assert writer.size() > 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_complete_recording_workflow(self):
        """Test complete workflow for creating a recording."""
        with th.create(server_name="Integration Test Server") as writer:
            # Setup
            num_players = 3
            for i in range(num_players):
                writer.write(th.Join(i))
                writer.write(th.PlayerName(i, f"Player_{i}"))
                writer.write(th.PlayerReady(i))
                writer.write(th.PlayerNew(i, i * 100, 200))

            # Game events
            writer.write(th.TickSkip(300))
            for i in range(num_players):
                writer.write(th.PlayerDiff(i, 10, -5))

            # End game
            writer.write(th.TickSkip(300))
            for i in range(num_players):
                writer.write(th.PlayerOld(i))
                writer.write(th.Drop(i, "finish"))

            assert writer.size() > 0

    def test_batch_creation_performance(self):
        """Test batch creation of many chunks."""
        chunks = []
        for i in range(100):
            chunks.extend(
                [
                    th.Join(i),
                    th.PlayerName(i, f"Player{i:03d}"),
                    th.TickSkip(10),
                ]
            )

        writer = th.create()
        writer.write_all(chunks)
        assert writer.size() > 0

    def test_headers_and_content_combination(self):
        """Test combining headers with content."""
        writer = th.create(
            server_name="Combo Server", comment="Integration test", game_type="DDRace"
        )
        writer.update_headers({"map_name": "Combo Map", "version": "1.0"})
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player"))
        writer.write(th.Eos())

        data = writer.getvalue()
        assert isinstance(data, bytes)
        assert len(data) > 0


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_chunk_sequence(self):
        """Test sequence with minimal chunks."""
        writer = th.create()
        writer.write(th.Eos())
        assert writer.size() > 0

    def test_special_characters_in_headers(self):
        """Test headers with special characters."""
        writer = th.create()
        writer.set_header("comment", "Special: !@#$%^&*()[]{}\"'")
        writer.write(th.Join(0))
        assert writer.size() > 0

    def test_special_characters_in_names(self):
        """Test player names with special characters."""
        writer = th.create()
        writer.write(th.Join(0))
        writer.write(th.PlayerName(0, "Player™©®"))
        assert writer.size() > 0

    def test_large_message_content(self):
        """Test writing large messages."""
        writer = th.create()
        writer.write(th.Join(0))
        large_message = "x" * 10000
        writer.write(th.NetMessage(0, large_message))
        assert writer.size() > 0

    def test_many_tick_skips(self):
        """Test many tick skip events."""
        writer = th.create()
        for _ in range(1000):
            writer.write(th.TickSkip(1))
        assert writer.size() > 0
