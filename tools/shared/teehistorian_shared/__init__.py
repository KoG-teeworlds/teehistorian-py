"""Shared utilities for teehistorian tools."""

from .config import (
    get_s3_config,
    get_download_dir,
    clear_config_cache,
    CONFIG_FILENAME,
)
from .exceptions import (
    TeehistorianToolsError,
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    S3Error,
)

__version__ = "0.1.0"

__all__ = [
    "get_s3_config",
    "get_download_dir",
    "clear_config_cache",
    "CONFIG_FILENAME",
    "TeehistorianToolsError",
    "ConfigurationError",
    "ConnectionError",
    "NotFoundError",
    "S3Error",
]
