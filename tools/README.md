# Teehistorian Tools

Separate utilities for working with teehistorian files.

## Structure

```
tools/
├── shared/                     # Shared config and exceptions
├── teehistorian-downloader/    # Download teehistorian files from S3/Minio
├── teehistorian-header/        # Parse and display teehistorian headers
├── teehistorian-map/           # Download maps from S3/R2
└── teehistorian-demo/          # Convert teehistorian to demo files
```

## Installation

Install all tools from the workspace:

```bash
cd tools
uv sync
```

All commands are now available:
- `teehistorian-header`
- `teehistorian-downloader`
- `teehistorian-map`
- `teehistorian-demo`

## Configuration

Create `~/.teehistorian.toml`:

```toml
[teehistorian.s3]
endpoint = "https://minio.example.com"
access_key = "your-access-key"  # optional for public buckets
secret_key = "your-secret-key"  # optional for public buckets
bucket = "teehistorian"

[teehistorian]
download_dir = "/path/to/teehistorian/downloads"  # optional

[maps.s3]
endpoint = "https://xxx.r2.cloudflarestorage.com"
access_key = "your-r2-access-key"  # optional for public buckets
secret_key = "your-r2-secret-key"  # optional for public buckets
bucket = "maps"
pattern = "{map_name}_{map_sha256}.map"  # optional, this is default

[maps]
download_dir = "/path/to/map/downloads"  # optional
```

Or use environment variables:

| Profile | Variables |
|---------|-----------|
| teehistorian | `TEEHISTORIAN_S3_ENDPOINT`, `TEEHISTORIAN_S3_ACCESS_KEY`, `TEEHISTORIAN_S3_SECRET_KEY`, `TEEHISTORIAN_S3_BUCKET`, `TEEHISTORIAN_DOWNLOAD_DIR` |
| maps | `MAPS_S3_ENDPOINT`, `MAPS_S3_ACCESS_KEY`, `MAPS_S3_SECRET_KEY`, `MAPS_S3_BUCKET`, `MAPS_S3_PATTERN`, `MAPS_DOWNLOAD_DIR` |

## CLI Usage

```bash
# Parse header
teehistorian-header recording.teehistorian
teehistorian-header recording.teehistorian -f table
teehistorian-header recording.teehistorian -f raw

# Download teehistorian file
teehistorian-downloader 000c81cc-0922-4150-97e9-cd8f9776eb8e
teehistorian-downloader 000c81cc-0922-4150-97e9-cd8f9776eb8e -o /tmp

# Download map from teehistorian
teehistorian-map recording.teehistorian
teehistorian-map recording.teehistorian --pattern "{map_sha256}.map"

# Convert teehistorian to demo (requires tee-hee installed)
teehistorian-demo recording.teehistorian
teehistorian-demo 000c81cc-0922-4150-97e9-cd8f9776eb8e  # download by UUID
teehistorian-demo recording.teehistorian -o output.demo
teehistorian-demo recording.teehistorian -m local_map.map  # use local map
```

## Python API

```python
# Header parsing
from teehistorian_header import parse_header, get_header
header = parse_header("recording.teehistorian")
print(header["map_name"])

# Teehistorian download
from teehistorian_downloader import download
data = download("000c81cc-0922-4150-97e9-cd8f9776eb8e")
path = download("000c81cc-...", save=True)

# Map download
from teehistorian_map import download_map
map_data = download_map("recording.teehistorian")
path = download_map("recording.teehistorian", save=True)
```
