"""Shared exceptions for teehistorian tools."""


class TeehistorianToolsError(Exception):
    """Base exception for teehistorian tools."""

    pass


class ConfigurationError(TeehistorianToolsError):
    """Raised when required configuration is missing."""

    pass


class ConnectionError(TeehistorianToolsError):
    """Raised when connection to S3 fails."""

    pass


class NotFoundError(TeehistorianToolsError):
    """Raised when the requested file doesn't exist."""

    pass


class S3Error(TeehistorianToolsError):
    """Raised for general S3 errors."""

    pass
