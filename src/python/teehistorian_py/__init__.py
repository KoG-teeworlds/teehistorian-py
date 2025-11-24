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
    CustomChunk,
    Generic,
    Teehistorian,
    TeehistorianError,
    Unknown,
)
from ._rust import (
    # Chunk types - directly imported
    PyAntiBot as AntiBot,
)
from ._rust import (
    PyAuthLogin as AuthLogin,
)
from ._rust import (
    PyConsoleCommand as ConsoleCommand,
)
from ._rust import (
    PyDdnetVersion as DdnetVersion,
)
from ._rust import (
    PyDrop as Drop,
)
from ._rust import (
    PyEos as Eos,
)
from ._rust import (
    PyInputDiff as InputDiff,
)
from ._rust import (
    PyInputNew as InputNew,
)
from ._rust import (
    PyJoin as Join,
)
from ._rust import (
    PyJoinVer6 as JoinVer6,
)
from ._rust import (
    PyNetMessage as NetMessage,
)
from ._rust import (
    PyPlayerDiff as PlayerDiff,
)
from ._rust import (
    PyPlayerName as PlayerName,
)
from ._rust import (
    PyPlayerNew as PlayerNew,
)
from ._rust import (
    PyPlayerOld as PlayerOld,
)
from ._rust import (
    PyPlayerReady as PlayerReady,
)
from ._rust import (
    PyPlayerTeam as PlayerTeam,
)
from ._rust import (
    PyTeamLoadFailure as TeamLoadFailure,
)
from ._rust import (
    PyTeamLoadSuccess as TeamLoadSuccess,
)
from ._rust import (
    PyTickSkip as TickSkip,
)
from ._rust import (
    TeehistorianWriter as RustTeehistorianWriter,
)


# Define temporary exception classes for compatibility
class ParseError(TeehistorianError):
    pass


class ValidationError(TeehistorianError):
    pass


class FileError(TeehistorianError):
    pass


class WriteError(TeehistorianError):
    pass


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


class TeehistorianWriter:
    """
    Pythonic teehistorian file writer with context manager support.

    This class provides a clean, high-level interface for creating teehistorian files
    following Python best practices.
    """

    def __init__(self):
        """Initialize a new teehistorian writer."""
        self._writer = RustTeehistorianWriter()
        self._closed = False

    def __enter__(self) -> "TeehistorianWriter":
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager, automatically writing EOS if not already present."""
        if not self._closed:
            # Automatically write EOS chunk when exiting context
            try:
                self.write(Eos())
            except Exception:
                pass  # Don't fail if EOS was already written
            self._closed = True

    def write(self, chunk) -> "TeehistorianWriter":
        """
        Write a chunk to the teehistorian file.

        Args:
            chunk: A chunk object (Join, Drop, PlayerNew, etc.)

        Returns:
            Self for method chaining

        Example:
            >>> writer.write(th.Join(0)).write(th.PlayerName(0, "Player"))
        """
        if self._closed:
            raise ValueError("Cannot write to closed writer")
        self._writer.write(chunk)
        return self

    def write_all(self, chunks) -> "TeehistorianWriter":
        """
        Write multiple chunks at once.

        Args:
            chunks: Iterable of chunk objects

        Returns:
            Self for method chaining
        """
        for chunk in chunks:
            self.write(chunk)
        return self

    def set_header(self, key: str, value: str) -> "TeehistorianWriter":
        """
        Set a header field.

        Args:
            key: Header field name
            value: Header field value

        Returns:
            Self for method chaining

        Example:
            >>> writer.set_header("server_name", "My Server")
        """
        if self._closed:
            raise ValueError("Cannot modify header of closed writer")
        self._writer.set_header(key, value)
        return self

    def get_header(self, key: str) -> Union[str, None]:
        """
        Get a header field value.

        Args:
            key: Header field name

        Returns:
            Header field value or None if not set

        Example:
            >>> value = writer.get_header("server_name")
        """
        return self._writer.get_header(key)

    def update_headers(self, headers: dict) -> "TeehistorianWriter":
        """
        Update multiple header fields.

        Args:
            headers: Dictionary of header fields

        Returns:
            Self for method chaining

        Example:
            >>> writer.update_headers({
            ...     "server_name": "My Server",
            ...     "comment": "Generated by script"
            ... })
        """
        for key, value in headers.items():
            self.set_header(key, value)
        return self

    def save(self, path: Union[str, PathLike[str]]) -> None:
        """
        Save the teehistorian to a file.

        Args:
            path: File path to save to

        Example:
            >>> writer.save("output.teehistorian")
        """
        self._writer.save(str(path))

    def getvalue(self) -> bytes:
        """
        Get the teehistorian data as bytes.

        Returns:
            Complete teehistorian file as bytes

        Example:
            >>> data = writer.getvalue()
            >>> with open("file.teehistorian", "wb") as f:
            ...     f.write(data)
        """
        return self._writer.getvalue()

    def writeto(self, file) -> None:
        """
        Write the teehistorian to a file-like object.

        Args:
            file: File-like object with write() method

        Example:
            >>> with open("output.teehistorian", "wb") as f:
            ...     writer.writeto(f)
        """
        self._writer.writeto(file)

    def size(self) -> int:
        """Get the current size of the teehistorian data in bytes."""
        return self._writer.size()

    def is_empty(self) -> bool:
        """Check if any data has been written."""
        return self._writer.is_empty()

    def reset(self) -> None:
        """Reset the writer to initial empty state."""
        self._writer.reset()
        self._closed = False

    def __repr__(self) -> str:
        status = (
            "closed" if self._closed else ("empty" if self.is_empty() else "active")
        )
        return f"TeehistorianWriter(size={self.size()}, status={status})"


def create(**headers) -> TeehistorianWriter:
    """
    Create a new teehistorian writer.

    This is the recommended way to create new teehistorian files.

    Args:
        **headers: Optional header fields to set immediately

    Returns:
        TeehistorianWriter instance

    Example:
        >>> # Basic usage
        >>> with th.create() as writer:
        ...     writer.write(th.Join(0))
        ...     writer.write(th.PlayerName(0, "Player"))
        ...     # EOS is automatically written on exit

        >>> # With headers
        >>> with th.create(server_name="My Server", comment="Test file") as writer:
        ...     writer.write(th.Join(0))

        >>> # Save to file
        >>> with th.create() as writer:
        ...     writer.write(th.Join(0))
        ...     writer.save("output.teehistorian")

        >>> # Method chaining
        >>> writer = (th.create()
        ...     .set_header("server_name", "My Server")
        ...     .write(th.Join(0))
        ...     .write(th.PlayerName(0, "Player")))
    """
    writer = TeehistorianWriter()
    if headers:
        writer.update_headers(headers)
    return writer


__all__ = [
    # Core parsing interface
    "Teehistorian",
    "TeehistorianParser",  # Alias for Teehistorian
    "parse",  # Modern file parser
    "open",  # Alias for parse
    # Core writing interface
    "TeehistorianWriter",
    "create",  # Modern writer creator
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
    "WriteError",
    # Utilities
    "calculate_uuid",
    "format_uuid_from_bytes",
    # Version info
    "__version__",
]
