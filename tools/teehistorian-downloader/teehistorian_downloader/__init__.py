"""Download teehistorian files from S3/Minio."""

from .downloader import download

# Re-export exceptions from shared
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)

__version__ = "0.1.0"

__all__ = [
    "download",
    "ConfigurationError",
    "ConnectionError",
    "NotFoundError",
    "S3Error",
]
