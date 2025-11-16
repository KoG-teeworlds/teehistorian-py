# Type stubs for teehistorian_py._rust
# This file provides type hints for the Rust extension module

from typing import Any, Iterator, Optional, List, Dict, Union, Protocol

__version__: str
__doc__: str

class TeehistorianError(Exception):
    """Base exception for all teehistorian parsing errors"""
    def __init__(self, message: str) -> None: ...

class Teehistorian:
    """Main teehistorian parser class

    This class provides high-performance parsing of teehistorian files
    using the Rust backend. It supports iteration over chunks and
    custom UUID handler registration.
    """

    def __init__(self, data: bytes) -> None:
        """Initialize parser with raw teehistorian data

        Args:
            data: Raw bytes from a teehistorian file

        Raises:
            TeehistorianError: If data is empty or initialization fails
        """
        ...

    def register_custom_uuid(self, uuid_string: str) -> None:
        """Register a custom UUID handler

        Args:
            uuid_string: UUID string in format XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

        Raises:
            TeehistorianError: If UUID format is invalid or registration fails
        """
        ...

    def header(self) -> bytes:
        """Get the teehistorian header as raw bytes

        Returns:
            Header data as bytes (typically JSON)

        Raises:
            TeehistorianError: If header parsing fails
        """
        ...

    @property
    def chunk_count(self) -> int:
        """Get the current number of processed chunks

        Returns:
            Number of chunks processed so far
        """
        ...

    def get_registered_uuids(self) -> List[str]:
        """Get list of all registered UUID handlers

        Returns:
            List of registered UUID strings
        """
        ...

    def __iter__(self) -> 'Teehistorian':
        """Iterator protocol support"""
        ...

    def __next__(self) -> 'Chunk':
        """Get next chunk from the stream

        Returns:
            Next chunk object

        Raises:
            StopIteration: When end of stream is reached
            TeehistorianError: If parsing fails
        """
        ...

# Base chunk class
class Chunk:
    """Base class for all teehistorian chunks

    All chunk types inherit from this base class, providing
    a common interface for chunk operations.
    """

    def chunk_type(self) -> str:
        """Get the chunk type identifier"""
        ...

    def __repr__(self) -> str:
        """Get string representation for debugging"""
        ...

    def __str__(self) -> str:
        """Get human-readable string representation"""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation

        Returns:
            Dictionary with chunk data including 'type' field
        """
        ...

# Player lifecycle chunks
class Join(Chunk):
    """Player joins the server"""
    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class JoinVer6(Chunk):
    """Player joins with version 6 protocol"""
    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class Drop(Chunk):
    """Player disconnects from server"""
    client_id: int
    reason: str

    def __init__(self, client_id: int, reason: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class PlayerReady(Chunk):
    """Player becomes ready to play"""
    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Player state chunks
class PlayerNew(Chunk):
    """New player spawn position"""
    client_id: int
    x: int
    y: int

    def __init__(self, client_id: int, x: int, y: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class PlayerOld(Chunk):
    """Player leaves game (but not server)"""
    client_id: int

    def __init__(self, client_id: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class PlayerTeam(Chunk):
    """Player changes team"""
    client_id: int
    team: int

    def __init__(self, client_id: int, team: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class PlayerName(Chunk):
    """Player changes name"""
    client_id: int
    name: str

    def __init__(self, client_id: int, name: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class PlayerDiff(Chunk):
    """Player position difference/update"""
    client_id: int
    dx: int
    dy: int

    def __init__(self, client_id: int, dx: int, dy: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Input chunks
class InputNew(Chunk):
    """New player input state"""
    client_id: int
    input: str

    def __init__(self, client_id: int, input: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class InputDiff(Chunk):
    """Player input difference from previous state"""
    client_id: int
    input: List[int]

    def __init__(self, client_id: int, input: List[int]) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Communication chunks
class NetMessage(Chunk):
    """Network message from/to player"""
    client_id: int
    message: str

    def __init__(self, client_id: int, message: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class ConsoleCommand(Chunk):
    """Console command executed by player"""
    client_id: int
    flags: int
    command: str
    args: str

    def __init__(self, client_id: int, flags: int, command: str, args: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Authentication & version chunks
class AuthLogin(Chunk):
    """Player authentication/login"""
    client_id: int
    level: int
    name: str

    def __init__(self, client_id: int, level: int, name: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class DdnetVersion(Chunk):
    """DDNet client version information"""
    client_id: int
    connection_id: str
    version: int
    version_str: bytes

    def __init__(self, client_id: int, connection_id: str, version: int, version_str: bytes) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Server event chunks
class TickSkip(Chunk):
    """Server tick skip (time advancement)"""
    dt: int

    def __init__(self, dt: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class TeamLoadSuccess(Chunk):
    """Team save loaded successfully"""
    team: int
    save: str

    def __init__(self, team: int, save: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class TeamLoadFailure(Chunk):
    """Team save load failed"""
    team: int

    def __init__(self, team: int) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class AntiBot(Chunk):
    """Anti-bot system event"""
    data: str

    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Special chunks
class Eos(Chunk):
    """End of stream marker"""

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class Unknown(Chunk):
    """Unknown chunk with UUID"""
    uuid: str
    data: bytes

    def __init__(self, uuid: str, data: bytes) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def data_preview(self) -> str:
        """Get hex preview of data (first 32 bytes)"""
        ...

class CustomChunk(Chunk):
    """Custom chunk with registered handler"""
    uuid: str
    data: bytes
    handler_name: str

    def __init__(self, uuid: str, data: bytes, handler_name: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def data_preview(self) -> str:
        """Get hex preview of data (first 32 bytes)"""
        ...

class Generic(Chunk):
    """Generic/fallback chunk type"""
    data: str

    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Type unions for easier type checking
PlayerChunk = Union[
    Join, JoinVer6, Drop, PlayerReady, PlayerNew, PlayerOld,
    PlayerTeam, PlayerName, PlayerDiff, AuthLogin, DdnetVersion,
    ConsoleCommand, NetMessage, InputNew, InputDiff
]

ServerChunk = Union[
    TickSkip, TeamLoadSuccess, TeamLoadFailure, AntiBot, Eos
]

CustomChunkTypes = Union[CustomChunk, Unknown, Generic]

AnyChunk = Union[PlayerChunk, ServerChunk, CustomChunkTypes]

# Helper protocols for type checking
class ChunkProtocol(Protocol):
    """Protocol defining the chunk interface"""
    def chunk_type(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class PlayerChunkProtocol(ChunkProtocol):
    """Protocol for player-related chunks"""
    client_id: int

# Type guards for runtime type checking
def is_player_chunk(chunk: Chunk) -> bool:
    """Check if chunk is player-related

    Args:
        chunk: Chunk to check

    Returns:
        True if chunk has a client_id attribute
    """
    ...

def is_server_chunk(chunk: Chunk) -> bool:
    """Check if chunk is server-related

    Args:
        chunk: Chunk to check

    Returns:
        True if chunk is a server event
    """
    ...

def is_custom_chunk(chunk: Chunk) -> bool:
    """Check if chunk is custom/unknown

    Args:
        chunk: Chunk to check

    Returns:
        True if chunk is Custom, Unknown, or Generic type
    """
    ...
