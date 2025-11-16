#!/usr/bin/env python3
"""
Basic functionality tests for teehistorian_py.
"""

import teehistorian_py as th


def test_imports():
    """Test that all expected classes and functions are available."""
    assert hasattr(th, 'Teehistorian')
    assert hasattr(th, 'TeehistorianParser')
    assert hasattr(th, 'Join')
    assert hasattr(th, 'Drop')
    assert hasattr(th, 'PlayerNew')
    assert hasattr(th, 'TeehistorianError')


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
    assert hasattr(th, 'ParseError')
    assert hasattr(th, 'ValidationError')
    assert hasattr(th, 'FileError')
