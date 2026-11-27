window.BENCHMARK_DATA = {
  "lastUpdate": 1795772318778,
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
          "id": "488247b6cac812a02ee60b4208987ebcfe585aa5",
          "message": "perf: parse immutable Python bytes without copying (#18)",
          "timestamp": "2026-11-27T10:37:35+01:00",
          "tree_id": "34465e45ec8385dab7e48cbf2c229e23771c6030",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/488247b6cac812a02ee60b4208987ebcfe585aa5"
        },
        "date": 1795772318358,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 2652.697496956886,
            "unit": "iter/sec",
            "range": "stddev: 0.000009551135470097758",
            "extra": "mean: 376.97475914505037 usec\nrounds: 2433"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_write_generator",
            "value": 2919.5928871069323,
            "unit": "iter/sec",
            "range": "stddev: 0.000012446224141960525",
            "extra": "mean: 342.5135074194933 usec\nrounds: 2763"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_synthetic_player_diffs",
            "value": 1421.6468963153513,
            "unit": "iter/sec",
            "range": "stddev: 0.000022849335859064302",
            "extra": "mean: 703.4095474704844 usec\nrounds: 1443"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_file_backed_synthetic",
            "value": 1367.183839988404,
            "unit": "iter/sec",
            "range": "stddev: 0.00002206145660804445",
            "extra": "mean: 731.4305294952006 usec\nrounds: 1407"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_create_parser_from_python_bytes",
            "value": 755463.8404604592,
            "unit": "iter/sec",
            "range": "stddev: 3.867394761863349e-7",
            "extra": "mean: 1.3236900913622747 usec\nrounds: 137476"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_malformed_net_messages",
            "value": 9410.431699818444,
            "unit": "iter/sec",
            "range": "stddev: 0.000005888359896204697",
            "extra": "mean: 106.26505052040207 usec\nrounds: 8551"
          }
        ]
      }
    ]
  }
}