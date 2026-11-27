window.BENCHMARK_DATA = {
  "lastUpdate": 1795771733644,
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
          "id": "2425eb1f589f0d6efbf6abc5df18f428d65a07c5",
          "message": "feat: add bounded batch streaming APIs (#17)",
          "timestamp": "2026-11-27T10:27:58+01:00",
          "tree_id": "c0145fae942a1b6727a6c3359336cb6c15365382",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/2425eb1f589f0d6efbf6abc5df18f428d65a07c5"
        },
        "date": 1795771732534,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 4048.7641744443877,
            "unit": "iter/sec",
            "range": "stddev: 0.00000831557012608628",
            "extra": "mean: 246.9889469759572 usec\nrounds: 3621"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_write_generator",
            "value": 4402.744467889555,
            "unit": "iter/sec",
            "range": "stddev: 0.000008846228765478164",
            "extra": "mean: 227.1310559341518 usec\nrounds: 4255"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_synthetic_player_diffs",
            "value": 1682.3334602606838,
            "unit": "iter/sec",
            "range": "stddev: 0.000013622908902000505",
            "extra": "mean: 594.4124774437087 usec\nrounds: 1596"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_file_backed_synthetic",
            "value": 1688.4598531466688,
            "unit": "iter/sec",
            "range": "stddev: 0.000014632354318598326",
            "extra": "mean: 592.2557164367086 usec\nrounds: 1594"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_malformed_net_messages",
            "value": 11642.675147599577,
            "unit": "iter/sec",
            "range": "stddev: 0.00000438346075480341",
            "extra": "mean: 85.89091315548511 usec\nrounds: 10870"
          }
        ]
      }
    ]
  }
}