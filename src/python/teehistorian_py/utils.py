#!/usr/bin/env python3
"""Utility functions for teehistorian library."""

import uuid

TEEWORLDS_NAMESPACE = uuid.UUID("e05ddaaa-c4e6-4cfb-b642-5d48e80c0029")


def calculate_uuid(name: str) -> str:
    """Calculate UUID v3 from name using Teeworlds namespace.

    Args:
        name: The UUID name string (e.g., 'kog-one-login@kog.tw')

    Returns:
        Formatted UUID string in standard format

    Example:
        >>> calculate_uuid('teehistorian@ddnet.tw')
        '699db17b-8efb-34ff-b1d8-da6f60c15dd1'
    """
    return str(uuid.uuid3(TEEWORLDS_NAMESPACE, name))


def format_uuid_from_bytes(uuid_bytes: bytes) -> str:
    """Convert 16-byte UUID to standard string format.

    Args:
        uuid_bytes: 16-byte UUID data

    Returns:
        Formatted UUID string or "invalid-uuid" if malformed

    Example:
        >>> format_uuid_from_bytes(b'\\x69\\x9d\\xb1\\x7b...')
        '699db17b-...'
    """
    if len(uuid_bytes) != 16:
        return "invalid-uuid"
    try:
        return str(uuid.UUID(bytes=uuid_bytes))
    except ValueError:
        return "invalid-uuid"
