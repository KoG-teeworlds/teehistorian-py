"""Regression tests for parser resource limits and hostile input handling."""

from __future__ import annotations

import json

import pytest

import teehistorian_py as th
from teehistorian_py import _rust


MAGIC = bytes.fromhex("699db17b8efb34ffb1d8da6f60c15dd1")


def recording(header: dict[str, object], chunks: bytes = b"\x40") -> bytes:
    return MAGIC + json.dumps(header, separators=(",", ":")).encode() + b"\0" + chunks


def test_rejects_oversized_input_before_copying() -> None:
    data = recording({"version": "2"})
    with pytest.raises(_rust.ValidationError, match="max_input_bytes"):
        _rust.Teehistorian(data, max_input_bytes=len(data) - 1)


def test_rejects_zero_limits() -> None:
    data = recording({"version": "2"})
    with pytest.raises(_rust.ValidationError, match="max_chunks must be greater than zero"):
        _rust.Teehistorian(data, max_chunks=0)


def test_rejects_oversized_and_truncated_headers() -> None:
    with pytest.raises(_rust.ValidationError, match="max_header_bytes"):
        _rust.Teehistorian(recording({"comment": "x" * 100}), max_header_bytes=32)

    with pytest.raises(_rust.ValidationError, match="missing NUL terminator"):
        _rust.Teehistorian(MAGIC + b"{}")


def test_enforces_chunk_limit_incrementally() -> None:
    writer = th.TeehistorianWriter()
    writer.write(th.Join(1)).write(th.Join(2))
    parser = _rust.Teehistorian(writer.getvalue(), max_chunks=1)

    assert next(parser).client_id == 1
    with pytest.raises(_rust.ValidationError, match="Chunk limit exceeded"):
        next(parser)


def test_cached_header_remains_safe_after_iteration_starts() -> None:
    data = recording({"version": "2"})
    parser = _rust.Teehistorian(data)
    next(parser)

    assert parser.header() == b'{"version":"2"}'
    assert parser.get_header_str() == '{"version":"2"}'


def test_parser_owns_temporary_python_bytes() -> None:
    parser = _rust.Teehistorian(recording({"version": "2"}))
    assert isinstance(next(parser), th.Eos)


def test_mutable_bytearray_is_safely_snapshotted() -> None:
    data = bytearray(recording({"version": "2"}))
    parser = _rust.Teehistorian(data)
    data[:] = b"x" * len(data)

    assert isinstance(next(parser), th.Eos)


def test_rejects_oversized_network_message() -> None:
    writer = th.TeehistorianWriter()
    writer.write(th.NetMessage(1, b"x" * 65))
    parser = _rust.Teehistorian(writer.getvalue(), max_net_message_bytes=64)

    with pytest.raises(_rust.ValidationError, match="max_net_message_bytes"):
        next(parser)


def test_metadata_validation_is_transactional() -> None:
    valid_uuid = "92f0f7de-d1e4-4f3e-8203-e914aa6a1407"
    _rust.unregister_global_chunk(valid_uuid)
    data = recording(
        {
            "version": "2",
            "__teehistorian_py": {
                "chunks": {
                    valid_uuid: {"name": "Valid", "fields": {}},
                    "not-a-uuid": {"name": "Invalid", "fields": {}},
                }
            },
        }
    )

    with pytest.raises(_rust.ValidationError, match="Invalid metadata UUID"):
        _rust.Teehistorian(data)
    assert _rust.get_global_chunk(valid_uuid) is None


def test_metadata_resource_limits() -> None:
    uuid = "a99775e0-9f25-4a3e-b0a6-b91f31ac1398"
    data = recording(
        {
            "version": "2",
            "__teehistorian_py": {
                "chunks": {
                    uuid: {
                        "name": "Wide",
                        "fields": {
                            "one": {"format": "Varint"},
                            "two": {"format": "Varint"},
                        },
                    }
                }
            },
        }
    )

    with pytest.raises(_rust.ValidationError, match="max_fields_per_chunk"):
        _rust.Teehistorian(data, max_fields_per_chunk=1)


def test_single_byte_chunk_corpus_never_panics() -> None:
    """A small exhaustive fuzz corpus for every possible one-byte chunk tail."""
    for byte in range(256):
        parser = _rust.Teehistorian(recording({"version": "2"}, bytes([byte])))
        try:
            list(parser)
        except _rust.TeehistorianError:
            pass


def test_malformed_network_messages_do_not_write_warnings(capfd: pytest.CaptureFixture[str]) -> None:
    writer = th.TeehistorianWriter()
    writer.write(th.NetMessage(1, b"\xff" * 8))
    list(_rust.Teehistorian(writer.getvalue()))

    captured = capfd.readouterr()
    assert "WARN:" not in captured.out
    assert "WARN:" not in captured.err
