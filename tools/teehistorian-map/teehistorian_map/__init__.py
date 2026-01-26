"""Download map files from S3/R2 based on teehistorian headers."""

from .map_downloader import download_map, get_map_url

# Re-export exceptions from shared
from teehistorian_shared import (
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)

__version__ = "0.1.0"

__all__ = [
    "download_map",
    "ConfigurationError",
    "ConnectionError",
    "NotFoundError",
    "S3Error",
]
