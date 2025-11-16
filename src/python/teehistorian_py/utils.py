#!/usr/bin/env python3
"""
Utility functions for teehistorian library.

This module contains helper functions for common operations
like UUID calculation, data formatting, and validation.
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

# Teeworlds namespace UUID for calculating UUIDs
TEEWORLDS_NAMESPACE = bytes(
    [
        0xE0,
        0x5D,
        0xDA,
        0xAA,
        0xC4,
        0xE6,
        0x4C,
        0xFB,
        0xB6,
        0x42,
        0x5D,
        0x48,
        0xE8,
        0x0C,
        0x00,
        0x29,
    ]
)


def calculate_uuid(name: str) -> str:
    """Calculate UUID v3 from name using Teeworlds namespace.

    This function implements UUID version 3 (MD5-based) using the
    Teeworlds namespace for generating deterministic UUIDs from names.

    Args:
        name: The UUID name string (e.g., 'kog-one-login@kog.tw')

    Returns:
        Formatted UUID string in standard format

    Raises:
        ValidationError: If name is invalid

    Example:
        >>> calculate_uuid('kog-one-login@kog.tw')
        'a1b2c3d4-e5f6-3789-8abc-def012345678'
    """
    if not name:
        return "invalid-uuid"

    md5 = hashlib.md5()
    md5.update(TEEWORLDS_NAMESPACE)
    md5.update(name.encode("utf-8"))
    digest = md5.digest()

    # Convert to UUID v3 format
    uuid_bytes = bytearray(digest[:16])

    # Set version (4 bits) to 3
    uuid_bytes[6] &= 0x0F
    uuid_bytes[6] |= 0x30

    # Set variant (2 bits) to 10
    uuid_bytes[8] &= 0x3F
    uuid_bytes[8] |= 0x80

    return format_uuid_from_bytes(bytes(uuid_bytes))


def format_uuid_from_bytes(uuid_bytes: bytes) -> str:
    """Convert 16-byte UUID to standard string format.

    Takes raw 16-byte UUID data and formats it as a standard
    UUID string with hyphens in the correct positions.

    Args:
        uuid_bytes: 16-byte UUID data

    Returns:
        Formatted UUID string or "invalid-uuid" if malformed

    Example:
        >>> uuid_bytes = b'\\x12\\x34\\x56\\x78\\x9a\\xbc...'  # 16 bytes
        >>> format_uuid_from_bytes(uuid_bytes)
        '12345678-9abc-def0-1234-567890abcdef'
    """
    if len(uuid_bytes) != 16:
        logger.warning(f"Invalid UUID bytes length: {len(uuid_bytes)}, expected 16")
        return "invalid-uuid"

    try:
        return (
            f"{uuid_bytes[0:4].hex()}-{uuid_bytes[4:6].hex()}-"
            f"{uuid_bytes[6:8].hex()}-{uuid_bytes[8:10].hex()}-{uuid_bytes[10:16].hex()}"
        )
    except Exception as e:
        logger.warning(f"Failed to format UUID bytes: {e}")
        return "invalid-uuid"
