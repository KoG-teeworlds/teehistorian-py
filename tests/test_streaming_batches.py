"""Tests for bounded pull batches and lazy writer input."""

from __future__ import annotations

from pathlib import Path

import pytest

import teehistorian_py as th
from teehistorian_py import _rust


def recording_with_joins(count: int) -> bytes:
    writer = th.TeehistorianWriter()
    writer.write_all(th.Join(i) for i in range(count))
    writer.write(th.Eos())
    return writer.getvalue()


def test_next_batch_is_bounded_and_resumable() -> None:
    parser = th.Teehistorian(recording_with_joins(5))

    assert [chunk.client_id for chunk in parser.next_batch(2)] == [0, 1]
    assert [chunk.client_id for chunk in parser.next_batch(2)] == [2, 3]
    final = parser.next_batch(2)
    assert final[0].client_id == 4
    assert isinstance(final[1], th.Eos)
    assert parser.next_batch(2) == []


@pytest.mark.parametrize("max_items", [0, 65_537])
def test_next_batch_rejects_unbounded_sizes(max_items: int) -> None:
    parser = th.Teehistorian(recording_with_joins(1))
    with pytest.raises(th.ValidationError, match="max_items must be between"):
        parser.next_batch(max_items)


def test_rust_writer_consumes_generators_lazily() -> None:
    consumed: list[int] = []

    def chunks():
        for client_id in range(5):
            consumed.append(client_id)
            yield th.Join(client_id)

    writer = _rust.TeehistorianWriter()
    writer.write_all(chunks())
    writer.write(th.Eos())

    assert consumed == [0, 1, 2, 3, 4]
    parsed = list(th.Teehistorian(writer.getvalue()))
    assert [chunk.client_id for chunk in parsed[:-1]] == consumed
    assert isinstance(parsed[-1], th.Eos)


def test_parse_helper_uses_file_backed_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "recording.teehistorian"
    data = recording_with_joins(5)
    path.write_bytes(data)

    def fail_eager_read(_path: Path) -> bytes:
        raise AssertionError("parse() must not eagerly call Path.read_bytes()")

    monkeypatch.setattr(Path, "read_bytes", fail_eager_read)
    parsed = list(th.parse(path))
    assert [chunk.client_id for chunk in parsed[:-1]] == list(range(5))
    assert isinstance(parsed[-1], th.Eos)


def test_file_stream_enforces_limits_before_iteration(tmp_path: Path) -> None:
    path = tmp_path / "recording.teehistorian"
    data = recording_with_joins(1)
    path.write_bytes(data)

    with pytest.raises(th.ValidationError, match="max_input_bytes"):
        th.Teehistorian.from_file(path, max_input_bytes=len(data) - 1)
    with pytest.raises(th.ValidationError, match="File-backed max_header_bytes"):
        th.Teehistorian.from_file(path, max_header_bytes=4 * 1024 * 1024)


def test_file_stream_rejects_truncated_header(tmp_path: Path) -> None:
    path = tmp_path / "truncated.teehistorian"
    path.write_bytes(bytes.fromhex("699db17b8efb34ffb1d8da6f60c15dd1") + b"{}")

    with pytest.raises(th.ValidationError, match="missing NUL terminator"):
        th.Teehistorian.from_file(path)


def test_file_stream_rejects_chunks_larger_than_bounded_buffer(tmp_path: Path) -> None:
    writer = th.TeehistorianWriter()
    writer.write(th.NetMessage(1, b"x" * (4 * 1024 * 1024 + 1)))
    path = tmp_path / "oversized-chunk.teehistorian"
    path.write_bytes(writer.getvalue())

    parser = th.Teehistorian.from_file(path)
    with pytest.raises(th.ParseError, match="possible DOS"):
        next(parser)
