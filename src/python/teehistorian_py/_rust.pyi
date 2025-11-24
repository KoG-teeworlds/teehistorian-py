# Type stubs for teehistorian_py._rust
# Auto-generated from Rust source code by build.rs
# Do not edit manually

from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Union,
)

__version__: str
__doc__: str

# ============================================================================
# Exceptions
# ============================================================================

class TeehistorianError(Exception):
    """Base exception for all teehistorian parsing and writing errors.

    This exception is raised for any errors that occur during parsing,
    writing, or validation of teehistorian files.
    """

    def __init__(self, message: str) -> None: ...

# ============================================================================
# Parser
# ============================================================================

class Teehistorian:
    """High-performance teehistorian file parser.

    This class provides efficient parsing of teehistorian files using the
    Rust backend. It supports iteration over chunks and custom UUID handler
    registration for extensibility.
    """

    def __init__(self, data: bytes) -> None:
        """Initialize parser with raw teehistorian data.

        Args:
            data: Raw bytes from a teehistorian file

        Raises:
            TeehistorianError: If data is empty or invalid
        """

    def register_custom_uuid(self, uuid_string: str) -> None:
        """Register a custom UUID handler for chunk parsing.

        Args:
            uuid_string: UUID in format XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

        Raises:
            TeehistorianError: If UUID format is invalid
        """

    def header(self) -> bytes:
        """Get the teehistorian header as raw bytes.

        Returns:
            Header data as bytes (typically JSON)
        """

    @property
    def chunk_count(self) -> int:
        """Number of chunks processed so far."""

    def get_registered_uuids(self) -> List[str]:
        """Get all registered custom UUID handlers.

        Returns:
            List of registered UUID strings
        """

    def __iter__(self) -> Iterator[Any]:
        """Iterate over chunks in the teehistorian."""

    def __next__(self) -> Any:
        """Get next chunk from the stream.

        Returns:
            Next chunk object

        Raises:
            StopIteration: When end of stream is reached
        """

    def __enter__(self) -> 'Teehistorian':
        """Context manager entry."""

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit."""

# ============================================================================
# Writer
# ============================================================================

class TeehistorianWriter:
    """Writer for creating teehistorian files programmatically.

    This class provides functionality to create valid teehistorian files
    by writing chunks and configuring headers. Supports method chaining
    and context manager protocol for clean resource management.
    """

    def __init__(self, file: Optional[Any] = None) -> None:
        """Initialize a new teehistorian writer.

        Args:
            file: Optional file-like object (for future use)
        """

    def write(self, chunk: Any) -> 'TeehistorianWriter':
        """Write a chunk to the teehistorian.

        Args:
            chunk: A chunk object to write

        Returns:
            Self for method chaining
        """

    def write_all(self, chunks: List[Any]) -> 'TeehistorianWriter':
        """Write multiple chunks at once.

        Args:
            chunks: List of chunk objects to write

        Returns:
            Self for method chaining
        """

    def set_header(self, key: str, value: str) -> 'TeehistorianWriter':
        """Set a header field value.

        Args:
            key: Header field name
            value: Header field value

        Returns:
            Self for method chaining
        """

    def get_header(self, key: str) -> Optional[str]:
        """Get a header field value.

        Args:
            key: Header field name

        Returns:
            Header value or None if not set
        """

    def update_headers(self, headers: Dict[str, str]) -> 'TeehistorianWriter':
        """Update multiple header fields from a dictionary.

        Args:
            headers: Dictionary of field names to values

        Returns:
            Self for method chaining
        """

    def getvalue(self) -> bytes:
        """Get all written data as bytes.

        Returns:
            Complete teehistorian file as bytes
        """

    def save(self, path: str) -> None:
        """Save the teehistorian to a file.

        Args:
            path: File path to save to
        """

    def writeto(self, file: Any) -> None:
        """Write all data to a file-like object.

        Args:
            file: File-like object with write() method
        """

    def size(self) -> int:
        """Get current buffer size in bytes.

        Returns:
            Number of bytes written
        """

    def reset(self) -> None:
        """Reset the writer to initial empty state.

        Clears all written data and resets headers to defaults.
        """

    def is_empty(self) -> bool:
        """Check if any data has been written.

        Returns:
            True if nothing has been written yet
        """

    def __enter__(self) -> 'TeehistorianWriter':
        """Context manager entry."""

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        """Context manager exit."""

    def __repr__(self) -> str:
        """Get string representation."""

# ============================================================================
# Chunk Types
# ============================================================================

class Chunk:
    """Base class for all teehistorian chunk types.

    All chunk types inherit from this base class, providing a common
    interface for chunk operations and serialization.
    """

    def chunk_type(self) -> str:
        """Get the chunk type identifier."""

    def __repr__(self) -> str:
        """Get string representation for debugging."""

    def __str__(self) -> str:
        """Get human-readable string representation."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation.

        Returns:
            Dictionary with chunk data including 'type' field
        """

# Input Chunks
class InputDiff(Chunk):
    """Player input difference from previous state
Category: Input"""

    client_id: int
    input: List[int]

    def __init__(self, client_id: int, input: List[int]) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class InputNew(Chunk):
    """New player input state
Category: Input"""

    client_id: int
    input: List[int]

    def __init__(self, client_id: int, input: List[int]) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# Other Chunks
class CustomChunk(Chunk):
    """Custom chunk with registered handler"""

    uuid: str
    data: bytes
    handler_name: str

    def __init__(self, uuid: str, data: bytes, handler_name: str) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class Generic(Chunk):
    """Generic/fallback chunk type"""

    data: str

    def __init__(self, data: str) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

class Unknown(Chunk):
    """Unknown chunk with UUID (not registered)"""

    uuid: str
    data: bytes

    def __init__(self, uuid: str, data: bytes) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# PlayerLifecycle Chunks
class PlayerReady(Chunk):
    """Player becomes ready to play
Category: PlayerLifecycle"""

    client_id: int

    def __init__(self, client_id: int) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# PlayerState Chunks
class PlayerTeam(Chunk):
    """Player changes team
Category: PlayerState"""

    client_id: int
    team: int

    def __init__(self, client_id: int, team: int) -> None: ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def to_dict(self) -> Dict[str, Any]: ...

# ============================================================================
# Type Aliases and Categories
# ============================================================================

InputChunk = Union[
    InputDiff,
    InputNew
]

OtherChunk = Union[
    CustomChunk,
    Generic,
    Unknown
]

PlayerLifecycleChunk = Union[
    PlayerReady
]

PlayerStateChunk = Union[
    PlayerTeam
]

# All chunk types
AllChunks = Union[
    CustomChunk,
    Generic,
    InputDiff,
    InputNew,
    PlayerReady,
    PlayerTeam,
    Unknown
]

