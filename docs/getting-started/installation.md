# Installation

## Requirements

- Python 3.8 or higher
- pip

## Install from PyPI

The easiest way to install teehistorian-py is from PyPI:

```bash
pip install teehistorian-py
```

## Install from Source

If you want to install from source or contribute to development:

### Prerequisites

- Rust toolchain (1.70+)
- Python 3.8+
- pip

### Steps

1. Clone the repository:
```bash
git clone https://github.com/KoG-teeworlds/teehistorian-py.git
cd teehistorian-py
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install maturin:
```bash
pip install maturin
```

4. Build and install:
```bash
maturin develop --release
```

## Verify Installation

```python
import teehistorian_py as th
print(th.__version__)
```

## Troubleshooting

### Rust Not Found

If you get an error about Rust not being found, install it from [rustup.rs](https://rustup.rs/).

### Build Errors

Make sure you have the latest version of pip and maturin:
```bash
pip install --upgrade pip maturin
```
