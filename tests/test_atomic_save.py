"""Regression tests for crash-safe writer persistence."""

from __future__ import annotations

from pathlib import Path

import pytest

import teehistorian_py as th


def writer_with_recording() -> th.TeehistorianWriter:
    writer = th.TeehistorianWriter()
    writer.write(th.Join(7)).write(th.Eos())
    return writer


def test_save_atomically_replaces_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "recording.teehistorian"
    target.write_bytes(b"old partial data")

    writer_with_recording().save(target)

    parsed = list(th.Teehistorian(target.read_bytes()))
    assert parsed[0].client_id == 7
    assert isinstance(parsed[1], th.Eos)
    assert list(tmp_path.iterdir()) == [target]


def test_failed_persist_cleans_up_temporary_file(tmp_path: Path) -> None:
    writer = writer_with_recording()

    with pytest.raises(th.FileError, match="atomically replace"):
        writer.save(tmp_path)

    assert list(tmp_path.iterdir()) == []
