#!/usr/bin/env python3
"""
High-performance Python bindings for teehistorian parsing.

This module provides a clean Python interface to the Rust-based teehistorian parser.
"""

import logging
import os

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


__all__ = [
    # Core parsing interface
    "Teehistorian",
    "TeehistorianParser",  # Alias for Teehistorian
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
