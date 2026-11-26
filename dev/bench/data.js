window.BENCHMARK_DATA = {
  "lastUpdate": 1795730965920,
  "repoUrl": "https://github.com/KoG-teeworlds/teehistorian-py",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "avolicious@kog.tw",
            "name": "Avolicious",
            "username": "Avolicious"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "76448e0a80c1fe70ce55740b0ad4c70ea862fec0",
          "message": "fix(security): update Python and PyO3 dependencies (#9)\n\n* chore(deps): update virtualenv security fixes\n\n* fix(security): update PyO3 and repair CI environments\n\n* fix(ci): install extension before PR tests",
          "timestamp": "2026-11-26T23:08:37+01:00",
          "tree_id": "7b18a24c95d69ed9bced4de0b173c05a2dfe84d1",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/76448e0a80c1fe70ce55740b0ad4c70ea862fec0"
        },
        "date": 1795730965172,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 2611.2347780400064,
            "unit": "iter/sec",
            "range": "stddev: 0.000011083099201521643",
            "extra": "mean: 382.96058570060876 usec\nrounds: 2112"
          }
        ]
      }
    ]
  }
}