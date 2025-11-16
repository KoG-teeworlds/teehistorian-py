#!/usr/bin/env python3
"""
High-performance Python bindings for teehistorian parsing.

This module provides a clean Python interface to the Rust-based teehistorian parser.

Example:
    >>> import teehistorian_py as th
    >>>
    >>> # Parse from file path
    >>> parser = th.parse("demo.teehistorian")
    >>> for chunk in parser:
    ...     if isinstance(chunk, th.Join):
    ...         print(f"Player {chunk.client_id} joined")
    >>>
    >>> # Or from bytes directly
    >>> from pathlib import Path
    >>> parser = th.Teehistorian(Path("demo.teehistorian").read_bytes())
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from os import PathLike

# Import Rust components directly
from ._rust import (
    AntiBot,
    AuthLogin,
    ConsoleCommand,
    CustomChunk,
    DdnetVersion,
    Drop,
    Eos,
    FileError,
    Generic,
    InputDiff,
    InputNew,
    # Chunk types
    Join,
    JoinVer6,
    NetMessage,
    ParseError,
    PlayerDiff,
    PlayerName,
    PlayerNew,
    PlayerOld,
    PlayerReady,
    PlayerTeam,
    TeamLoadFailure,
    TeamLoadSuccess,
    Teehistorian,
    TeehistorianError,
    TickSkip,
    Unknown,
    ValidationError,
)

# Alias for compatibility
TeehistorianParser = Teehistorian

# Re-export utilities for convenience
from .utils import calculate_uuid, format_uuid_from_bytes

__version__ = "2.0.0"


# Modern Pythonic helpers
def parse(path: Union[str, PathLike[str]]) -> Teehistorian:
    """
    Parse a teehistorian file from a path.

    This is the recommended way to parse teehistorian files.

    Args:
        path: Path to the teehistorian file (str or Path object)

    Returns:
        Teehistorian parser instance

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValidationError: If the file is not a valid teehistorian file
        ParseError: If parsing fails

    Example:
        >>> import teehistorian_py as th
        >>> parser = th.parse("demo.teehistorian")
        >>> for chunk in parser:
        ...     print(chunk)
    """
    return Teehistorian(Path(path).read_bytes())


def open(path: Union[str, PathLike[str]]) -> Teehistorian:
    """
    Open a teehistorian file for parsing.

    Alias for parse(). Provided for familiarity with Python's built-in open().
    Supports context manager protocol.

    Args:
        path: Path to the teehistorian file (str or Path object)

    Returns:
        Teehistorian parser instance

    Example:
        >>> import teehistorian_py as th
        >>>
        >>> # Simple usage
        >>> parser = th.open("demo.teehistorian")
        >>> for chunk in parser:
        ...     print(chunk)
        >>>
        >>> # With context manager
        >>> with th.open("demo.teehistorian") as parser:
        ...     for chunk in parser:
        ...         print(chunk)
    """
    return parse(path)


__all__ = [
    # Core parsing interface
    "Teehistorian",
    "TeehistorianParser",  # Alias for Teehistorian
    "parse",  # Modern file parser
    "open",  # Alias for parse
    # All chunk types
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
    # Exceptions
    "TeehistorianError",
    "ParseError",
    "ValidationError",
    "FileError",
    # Utilities
    "calculate_uuid",
    "format_uuid_from_bytes",
    # Version info
    "__version__",
]
