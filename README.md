# teehistorian-py

[![PyPI](https://badge.fury.io/py/teehistorian-py.svg)](https://pypi.org/project/teehistorian-py/)
[![CI](https://github.com/KoG-teeworlds/teehistorian-py/workflows/Build%20and%20Publish/badge.svg)](https://github.com/KoG-teeworlds/teehistorian-py/actions)
[![codecov](https://codecov.io/gh/KoG-teeworlds/teehistorian-py/branch/main/graph/badge.svg)](https://codecov.io/gh/KoG-teeworlds/teehistorian-py)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

High-performance Python bindings for parsing and writing Teeworlds/DDNet teehistorian files. Rust-powered, ~14M chunks/sec.

```bash
pip install teehistorian-py
```

## Reading

```python
import teehistorian_py as th

for chunk in th.parse("server.teehistorian"):
    match chunk:
        case th.Join(client_id=cid):
            print(f"Player {cid} joined")
        case th.PlayerName(client_id=cid, name=name):
            print(f"Player {cid}: {name}")
        case th.Drop(client_id=cid, reason=reason):
            print(f"Player {cid} left: {reason}")
```

## Writing

```python
import teehistorian_py as th

with th.create(server_name="My Server", map_name="dm1") as writer:
    writer.write(th.Join(0))
    writer.write(th.PlayerName(0, "Player 1"))
    writer.write(th.PlayerDiff(0, 10, 5))
    # EOS auto-written on exit

writer.save("output.teehistorian")
```

## Roundtrip (parse, modify, rewrite)

```python
import json
import teehistorian_py as th
from pathlib import Path

parser = th.Teehistorian(Path("original.teehistorian").read_bytes())
headers = json.loads(parser.get_header_str())

writer = th.create()
for k, v in headers.items():
    writer.set_header(k, json.dumps(v) if isinstance(v, (dict, list)) else str(v))

for chunk in parser:
    if isinstance(chunk, th.PlayerName):
        chunk = th.PlayerName(chunk.client_id, "Anon")
    writer.write(chunk)

writer.save("modified.teehistorian")
```

## Chunk Types

All validated chunk wrappers inherit from `ValidatedChunk` with coercive field validation.

| Category | Types |
|----------|-------|
| Player lifecycle | `Join`, `JoinVer6`, `Drop`, `PlayerReady` |
| Player state | `PlayerNew`, `PlayerOld`, `PlayerTeam`, `PlayerName`, `PlayerDiff` |
| Input | `InputNew`, `InputDiff` |
| Communication | `NetMessage`, `NetMessagePlayerInfo`, `ConsoleCommand` |
| Auth & version | `AuthLogin`, `DdnetVersion` |
| Server events | `TickSkip`, `TeamLoadSuccess`, `TeamLoadFailure`, `AntiBot` |
| Special | `Eos`, `Unknown`, `CustomChunk`, `Generic` |

## Benchmarks

```bash
pytest benchmarks/ --benchmark-only -v
./run-benchmarks.sh save      # save baseline
./run-benchmarks.sh compare   # compare against baseline
```

| Benchmark | Ops/sec | Mean |
|-----------|---------|------|
| Write 1000 chunks | ~3,500/s | ~282us |
| Roundtrip 1000 chunks | ~4,000/s | ~246us |
| Parse 1.9M chunks | ~7.6/s | ~132ms |

## Development

```bash
git clone https://github.com/KoG-teeworlds/teehistorian-py.git
cd teehistorian-py
pip install -e ".[dev]"
maturin develop --release
pytest tests/ -v
```

Requires Python 3.8+ and Rust 1.70+.

## License

AGPL-3.0 — see [LICENSE](LICENSE).

Built on [teehistorian](https://crates.io/crates/teehistorian) | Part of [KoG-teeworlds](https://github.com/KoG-teeworlds)
