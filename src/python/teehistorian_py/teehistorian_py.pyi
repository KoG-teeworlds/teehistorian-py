#!/usr/bin/env python3
"""
Type stubs for the teehistorian_py package.

Provides complete type hints for the Python wrapper around the Rust extension.
This helps IDEs and type checkers understand the API.
"""

from os import PathLike
from typing import Any, Dict, Iterator, List, Optional, Union

# ============================================================================
# Exceptions
# ============================================================================

class TeehistorianError(Exception):
    """Base exception for all teehistorian errors"""

    def __init__(self, message: str) -> None: ...

class ParseError(TeehistorianError):
    """Exception raised during parsing"""

    ...

class ValidationError(TeehistorianError):
    """Exception raised during validation"""

    ...

class FileError(TeehistorianError):
    """Exception raised for file I/O errors"""

    ...

class WriteError(TeehistorianError):
    """Exception raised during writing"""

    ...

# ============================================================================
# Core Parser Class
# ============================================================================

class Teehistorian:
    """High-performance teehistorian file parser"""

    def __init__(self, data: bytes) -> None:
        """Create parser from raw file data"""
        ...

    def register_custom_uuid(self, uuid_string: str) -> None:
        """Register a custom UUID handler"""
        ...

    def get_header_str(self) -> str:
        """Get the JSON header as a string (must be called before iterating chunks)"""
        ...

    def header(self) -> bytes:
        """Get the header as bytes"""
        ...

    def __iter__(self) -> Iterator[Any]:
        """Iterator support for processing chunks"""
        ...

    def __next__(self) -> Any:
        """Get next chunk"""
        ...

    def __enter__(self) -> "Teehistorian":
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

    def __init__(self, file: Optional[Any] = None) -> None:
        """Initialize a new teehistorian writer"""
        ...

    def __enter__(self) -> "TeehistorianWriter":
        """Context manager entry"""
        ...

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit"""
        ...

    def write(self, chunk: Any) -> "TeehistorianWriter":
        """Write a chunk to the teehistorian file"""
        ...

    def write_all(self, chunks: List[Any]) -> "TeehistorianWriter":
        """Write multiple chunks at once"""
        ...

    def set_header(self, key: str, value: str) -> "TeehistorianWriter":
        """Set a header field"""
        ...

    def get_header(self, key: str) -> Optional[str]:
        """Get a header field value"""
        ...

    def update_headers(self, headers: Dict[str, str]) -> "TeehistorianWriter":
        """Update multiple header fields from a dictionary"""
        ...

    def save(self, path: Union[str, PathLike[str]]) -> None:
        """Save the teehistorian to a file"""
        ...

    def getvalue(self) -> bytes:
        """Get all written data as bytes"""
        ...

    def writeto(self, file: Any) -> None:
        """Write all data to a file-like object"""
        ...

    @property
    def size(self) -> int:
        """Get the current size of the teehistorian data in bytes"""
        ...

    @property
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

def parse(path: Union[str, PathLike[str]]) -> Teehistorian:
    """Parse a teehistorian file from a path"""
    ...

def open(path: Union[str, PathLike[str]]) -> Teehistorian:
    """Open and parse a teehistorian file (alias for parse)"""
    ...

def create(**headers: str) -> TeehistorianWriter:
    """Create a new teehistorian writer with optional headers"""
    ...

def calculate_uuid(name: str) -> str:
    """Calculate a UUID from a chunk name"""
    ...

def format_uuid_from_bytes(data: bytes) -> str:
    """Format a UUID from 16 bytes"""
    ...

# ============================================================================
# Chunk Types - Player Lifecycle
# ============================================================================

class Join:
    """Player joins the game"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...

class JoinVer6:
    """Player joins with Teeworlds 0.6 protocol"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...

class Drop:
    """Player leaves the game"""

    client_id: int
    reason: str

    def __init__(self, client_id: int, reason: str) -> None: ...

class PlayerReady:
    """Player becomes ready to play"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...

# ============================================================================
# Chunk Types - Player State
# ============================================================================

class PlayerNew:
    """New player information"""

    client_id: int
    local: bool
    team: int

    def __init__(self, client_id: int, local: bool, team: int) -> None: ...

class PlayerOld:
    """Old player information"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...

class PlayerName:
    """Player's name"""

    client_id: int
    name: str

    def __init__(self, client_id: int, name: str) -> None: ...

class PlayerTeam:
    """Player changes team"""

    client_id: int
    team: int

    def __init__(self, client_id: int, team: int) -> None: ...

class PlayerDiff:
    """Difference in player state"""

    client_id: int
    dx: int
    dy: int

    def __init__(self, client_id: int, dx: int, dy: int) -> None: ...

# ============================================================================
# Chunk Types - Input
# ============================================================================

class InputNew:
    """New player input state"""

    client_id: int
    input: bytes

    def __init__(self, client_id: int, input: bytes) -> None: ...

class InputDiff:
    """Player input difference from previous state"""

    client_id: int
    input: bytes

    def __init__(self, client_id: int, input: bytes) -> None: ...

# ============================================================================
# Chunk Types - Communication
# ============================================================================

class NetMessage:
    """Network message from/to player"""

    client_id: int
    msg: bytes

    def __init__(self, client_id: int, msg: bytes) -> None: ...

class NetMessagePlayerInfo:
    """Parsed network message containing player information"""

    client_id: int
    message_type: str
    name: str
    clan: str
    country: int
    skin: str
    use_custom_color: bool
    color_body: int
    color_feet: int

    def __init__(
        self,
        client_id: int,
        message_type: str,
        name: str,
        clan: str,
        country: int,
        skin: str,
        use_custom_color: bool = False,
        color_body: int = 0,
        color_feet: int = 0,
    ) -> None: ...

class ConsoleCommand:
    """Console command executed"""

    client_id: int
    level: int
    name: str
    args: List[str]

    def __init__(
        self, client_id: int, level: int, name: str, args: List[str]
    ) -> None: ...

# ============================================================================
# Chunk Types - Authentication & Version
# ============================================================================

class AuthLogin:
    """Authentication login information"""

    client_id: int
    level: int
    auth_name: str

    def __init__(self, client_id: int, level: int, auth_name: str) -> None: ...

class DdnetVersion:
    """DDNet client version information"""

    client_id: int
    connection_id: str
    version: int
    version_str: bytes

    def __init__(
        self, client_id: int, connection_id: str, version: int, version_str: bytes
    ) -> None: ...

# ============================================================================
# Chunk Types - Game Events
# ============================================================================

class TickSkip:
    """Skip ticks in the game timeline"""

    ticks: int

    def __init__(self, ticks: int) -> None: ...

class TeamLoadSuccess:
    """Team file loaded successfully"""

    team_id: int
    team_name: str

    def __init__(self, team_id: int, team_name: str) -> None: ...

class TeamLoadFailure:
    """Failed to load team file"""

    team_id: int

    def __init__(self, team_id: int) -> None: ...

class AntiBot:
    """Anti-bot detection event"""

    detection_event: str

    def __init__(self, detection_event: str) -> None: ...

# ============================================================================
# Chunk Types - Special
# ============================================================================

class Eos:
    """End of stream marker"""

    def __init__(self) -> None: ...

class Unknown:
    """Unknown chunk with UUID (not registered)"""

    uuid: str
    data: bytes

    def __init__(self, uuid: str, data: bytes) -> None: ...

class CustomChunk:
    """Custom chunk with registered handler"""

    uuid: str
    data: bytes
    handler_name: str

    def __init__(self, uuid: str, data: bytes, handler_name: str) -> None: ...

class Generic:
    """Generic/fallback chunk type"""

    data: str

    def __init__(self, data: str) -> None: ...

# ============================================================================
# Type Aliases
# ============================================================================

PlayerLifecycleChunk = Union[Join, JoinVer6, Drop, PlayerReady]

PlayerStateChunk = Union[PlayerNew, PlayerOld, PlayerName, PlayerTeam, PlayerDiff]

InputChunk = Union[InputNew, InputDiff]

CommunicationChunk = Union[NetMessage, NetMessagePlayerInfo, ConsoleCommand]

AuthVersionChunk = Union[AuthLogin, DdnetVersion]

GameEventChunk = Union[TickSkip, TeamLoadSuccess, TeamLoadFailure, AntiBot]

SpecialChunk = Union[Eos, Unknown, CustomChunk, Generic]

AnyChunk = Union[
    Join,
    JoinVer6,
    Drop,
    PlayerReady,
    PlayerNew,
    PlayerOld,
    PlayerName,
    PlayerTeam,
    PlayerDiff,
    InputNew,
    InputDiff,
    NetMessage,
    NetMessagePlayerInfo,
    ConsoleCommand,
    AuthLogin,
    DdnetVersion,
    TickSkip,
    TeamLoadSuccess,
    TeamLoadFailure,
    AntiBot,
    Eos,
    Unknown,
    CustomChunk,
    Generic,
]

__version__: str
__all__: List[str]
