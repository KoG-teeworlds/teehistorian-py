window.BENCHMARK_DATA = {
  "lastUpdate": 1795770931444,
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
          "id": "be80c4837ebe42e520d6d85907a933c8d1033fd9",
          "message": "Merge pull request #16 from KoG-teeworlds/avolicious/parser-resource-limits\n\nsecurity: bound parser resources and hostile input",
          "timestamp": "2026-11-27T10:14:29+01:00",
          "tree_id": "004309976828f4a6ce1c605ba0243afea3e6504d",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/be80c4837ebe42e520d6d85907a933c8d1033fd9"
        },
        "date": 1795770931021,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 2687.7599529834856,
            "unit": "iter/sec",
            "range": "stddev: 0.000039937647881767895",
            "extra": "mean: 372.05703540971854 usec\nrounds: 1525"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_synthetic_player_diffs",
            "value": 1374.1336226611838,
            "unit": "iter/sec",
            "range": "stddev: 0.000011756389516430577",
            "extra": "mean: 727.7312653651348 usec\nrounds: 1383"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_malformed_net_messages",
            "value": 9855.168945467978,
            "unit": "iter/sec",
            "range": "stddev: 0.000003996798622971527",
            "extra": "mean: 101.46959484239612 usec\nrounds: 9268"
          }
        ]
      }
    ]
  }
}