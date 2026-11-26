window.BENCHMARK_DATA = {
  "lastUpdate": 1795728156481,
  "repoUrl": "https://github.com/KoG-teeworlds/teehistorian-py",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "41898282+github-actions[bot]@users.noreply.github.com",
            "name": "github-actions[bot]",
            "username": "github-actions[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2ef68919b0e064c3010b8bc050bd90e57ee8852a",
          "message": "chore: update Rust dependencies (#8)\n\nExact head 2316bcf119f49975f83bc68cc13eeaae649a189b passed rustfmt, strict Clippy, a release Maturin build on Python 3.14, and the full Python test suite (240 passed, 2 fixture-dependent skips).",
          "timestamp": "2026-11-26T22:21:50+01:00",
          "tree_id": "245d303ee374989c6aaf97a7ae2f801d966ccfc8",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/2ef68919b0e064c3010b8bc050bd90e57ee8852a"
        },
        "date": 1795728155713,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 2366.64313239156,
            "unit": "iter/sec",
            "range": "stddev: 0.00007208876833244359",
            "extra": "mean: 422.53941302484066 usec\nrounds: 2334"
          }
        ]
      }
    ]
  }
}