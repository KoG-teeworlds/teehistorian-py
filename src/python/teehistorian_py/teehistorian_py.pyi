#!/usr/bin/env python3
"""
Type stubs for the teehistorian_py package.

Provides complete type hints for the Python wrapper around the Rust extension.
This helps IDEs and type checkers understand the API.
"""

from os import PathLike
from typing import Any, Iterator, Protocol, Union, overload, runtime_checkable

# ============================================================================
# Protocols and Base Types
# ============================================================================

@runtime_checkable
class Chunk(Protocol):
    """Protocol for all chunk types"""

    def __repr__(self) -> str: ...

# ============================================================================
# Core Parser Class
# ============================================================================

class Teehistorian:
    """Main teehistorian parser class"""

    def __init__(self, data: bytes) -> None:
        """Create parser from raw file data"""
        ...

    def register_custom_uuid(self, uuid_string: str) -> None:
        """Register a custom UUID handler"""
        ...

    def header(self) -> bytes:
        """Get the JSON header as bytes"""
        ...

    def next_chunk(self) -> Union[Chunk, None]:
        """Get next chunk from the stream"""
        ...

    def __iter__(self) -> Iterator[Chunk]:
        """Iterator support for processing chunks"""
        ...

    def __next__(self) -> Chunk:
        """Get next chunk"""
        ...

    def __enter__(self) -> Teehistorian:
        """Context manager entry"""
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit"""
        ...

    def __repr__(self) -> str: ...

# ============================================================================
# Core Writer Class
# ============================================================================

class TeehistorianWriter:
    """Pythonic teehistorian file writer with context manager support"""

    def __init__(self) -> None:
        """Initialize a new teehistorian writer"""
        ...

    def __enter__(self) -> TeehistorianWriter:
        """Context manager entry"""
        ...

    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit"""
        ...

    def write(self, chunk: Any) -> TeehistorianWriter:
        """Write a chunk to the teehistorian file"""
        ...

    def write_all(self, chunks: list[Any]) -> TeehistorianWriter:
        """Write multiple chunks at once"""
        ...

    def set_header(self, key: str, value: str) -> TeehistorianWriter:
        """Set a header field"""
        ...

    def get_header(self, key: str) -> str | None:
        """Get a header field value"""
        ...

    def update_headers(self, headers: dict[str, str]) -> TeehistorianWriter:
        """Update multiple header fields from a dictionary"""
        ...

    def save(self, path: str | PathLike[str]) -> None:
        """Save the teehistorian to a file"""
        ...

    def getvalue(self) -> bytes:
        """Get all written data as bytes"""
        ...

    def writeto(self, file: Any) -> None:
        """Write all data to a file-like object"""
        ...

    def size(self) -> int:
        """Get the current size of the teehistorian data in bytes"""
        ...

    def is_empty(self) -> bool:
        """Check if any data has been written"""
        ...

    def reset(self) -> None:
        """Reset the writer to initial empty state"""
        ...

    def __repr__(self) -> str: ...

# ============================================================================
# Helper Functions
# ============================================================================

def parse(path: str | PathLike[str]) -> Teehistorian:
    """Parse a teehistorian file from a path"""
    ...

def open(path: str | PathLike[str]) -> Teehistorian:
    """Open and parse a teehistorian file"""
    ...

def create(**headers: str) -> TeehistorianWriter:
    """Create a new teehistorian writer"""
    ...

# ============================================================================
# Base Chunk Class
# ============================================================================

class BaseChunk:
    """Base class for all chunk types"""

    def __repr__(self) -> str: ...

# ============================================================================
# Time-related Chunks
# ============================================================================

class TickSkip(BaseChunk):
    """Represents a tick skip event"""

    dt: int

    def __init__(self, dt: int) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Player Connection Chunks
# ============================================================================

class Join(BaseChunk):
    """Player join chunk"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class JoinVer6(BaseChunk):
    """Version 6 join chunk"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class Drop(BaseChunk):
    """Player drop chunk"""

    client_id: int
    reason: str

    def __init__(self, client_id: int, reason: str) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Player State Chunks
# ============================================================================

class PlayerReady(BaseChunk):
    """Player ready state chunk"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerNew(BaseChunk):
    """New player spawn chunk"""

    client_id: int
    x: int
    y: int

    def __init__(self, client_id: int, x: int, y: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerOld(BaseChunk):
    """Player leaving chunk"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerTeam(BaseChunk):
    """Player team change chunk"""

    client_id: int
    team: int

    def __init__(self, client_id: int, team: int) -> None: ...
    def __repr__(self) -> str: ...

class PlayerName(BaseChunk):
    """Player name change chunk"""

    client_id: int
    name: str

    def __init__(self, client_id: int, name: str) -> None: ...
    def __repr__(self) -> str: ...

class PlayerDiff(BaseChunk):
    """Player position difference chunk"""

    client_id: int
    dx: int
    dy: int

    def __init__(self, client_id: int, dx: int, dy: int) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Authentication Chunks
# ============================================================================

class AuthLogin(BaseChunk):
    """Authentication login chunk"""

    client_id: int
    level: int
    name: str

    def __init__(self, client_id: int, level: int, name: str) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Version and Connection Info Chunks
# ============================================================================

class DdnetVersion(BaseChunk):
    """DDNet version information chunk"""

    client_id: int
    connection_id: str
    version: int
    version_str: Union[bytes, list[int]]

    def __init__(
        self,
        client_id: int,
        connection_id: str,
        version: int,
        version_str: Union[bytes, list[int]],
    ) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Command and Communication Chunks
# ============================================================================

class ConsoleCommand(BaseChunk):
    """Console command chunk"""

    client_id: int
    flags: int
    command: str
    args: str

    def __init__(self, client_id: int, flags: int, command: str, args: str) -> None: ...
    def __repr__(self) -> str: ...

class NetMessage(BaseChunk):
    """Network message chunk"""

    client_id: int
    message: str

    def __init__(self, client_id: int, message: str) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Input Chunks
# ============================================================================

class InputNew(BaseChunk):
    """New player input chunk"""

    client_id: int
    input: str

    def __init__(self, client_id: int, input: str) -> None: ...
    def __repr__(self) -> str: ...

class InputDiff(BaseChunk):
    """Input state difference chunk"""

    client_id: int
    input: list[int]

    def __init__(self, client_id: int, input: list[int]) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Team Management Chunks
# ============================================================================

class TeamLoadSuccess(BaseChunk):
    """Successful team load chunk"""

    team: int
    save: str

    def __init__(self, team: int, save: str) -> None: ...
    def __repr__(self) -> str: ...

class TeamLoadFailure(BaseChunk):
    """Failed team load chunk"""

    team: int

    def __init__(self, team: int) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Anti-bot Chunks
# ============================================================================

class AntiBot(BaseChunk):
    """AntiBot event chunk"""

    data: str

    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Special Chunks
# ============================================================================

class Eos(BaseChunk):
    """End of stream chunk"""

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...

class CustomChunk(BaseChunk):
    """Custom UUID chunk (registered)"""

    uuid: str
    data: bytes

    def __init__(self, uuid: str, data: bytes) -> None: ...
    def __repr__(self) -> str: ...

class Unknown(BaseChunk):
    """Unknown chunk type"""

    uuid: str
    data: bytes

    def __init__(self, uuid: str, data: bytes) -> None: ...
    def __repr__(self) -> str: ...

class Generic(BaseChunk):
    """Generic fallback chunk"""

    data: str

    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...

# ============================================================================
# Exception Types
# ============================================================================

class TeehistorianError(Exception):
    """Exception raised for teehistorian parsing errors"""

    def __init__(self, message: str) -> None: ...

class ParseError(TeehistorianError):
    """Parsing error"""

    ...

class ValidationError(TeehistorianError):
    """Validation error"""

    ...

class FileError(TeehistorianError):
    """File I/O error"""

    ...

class WriteError(TeehistorianError):
    """Writing error"""

    ...

# ============================================================================
# Type Aliases
# ============================================================================

PlayerChunk = Union[
    Join,
    JoinVer6,
    Drop,
    PlayerReady,
    PlayerNew,
    PlayerOld,
    PlayerTeam,
    PlayerName,
    PlayerDiff,
    AuthLogin,
    DdnetVersion,
    ConsoleCommand,
    NetMessage,
    InputNew,
    InputDiff,
]

ServerChunk = Union[TickSkip, TeamLoadSuccess, TeamLoadFailure, AntiBot, Eos]

CustomChunkTypes = Union[CustomChunk, Unknown, Generic]

AnyChunk = Union[PlayerChunk, ServerChunk, CustomChunkTypes]
