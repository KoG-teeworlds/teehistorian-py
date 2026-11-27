window.BENCHMARK_DATA = {
  "lastUpdate": 1795773012149,
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
          "id": "4d3257a289f93f1ef44c915bef52f53ef1b3ed54",
          "message": "security: save recordings with atomic replacement (#19)",
          "timestamp": "2026-11-27T10:48:57+01:00",
          "tree_id": "8ac8f9f7d797ac8c1a9c479b1cd2aa75ac06f62c",
          "url": "https://github.com/KoG-teeworlds/teehistorian-py/commit/4d3257a289f93f1ef44c915bef52f53ef1b3ed54"
        },
        "date": 1795773011286,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_benchmarks.py::test_write_chunks",
            "value": 2773.8670448821435,
            "unit": "iter/sec",
            "range": "stddev: 0.00004161463558549272",
            "extra": "mean: 360.5075455382859 usec\nrounds: 2174"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_write_generator",
            "value": 2836.926132036394,
            "unit": "iter/sec",
            "range": "stddev: 0.000015403499466346345",
            "extra": "mean: 352.4941974016726 usec\nrounds: 2771"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_synthetic_player_diffs",
            "value": 1364.4687302241439,
            "unit": "iter/sec",
            "range": "stddev: 0.000028139914751194818",
            "extra": "mean: 732.8859781460351 usec\nrounds: 1327"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_file_backed_synthetic",
            "value": 1346.309635400734,
            "unit": "iter/sec",
            "range": "stddev: 0.000026866134047051606",
            "extra": "mean: 742.7711825759505 usec\nrounds: 1320"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_create_parser_from_python_bytes",
            "value": 869467.9449187559,
            "unit": "iter/sec",
            "range": "stddev: 4.058020652512205e-7",
            "extra": "mean: 1.150128657237268 usec\nrounds: 175132"
          },
          {
            "name": "benchmarks/test_benchmarks.py::test_parse_malformed_net_messages",
            "value": 9385.848957608561,
            "unit": "iter/sec",
            "range": "stddev: 0.00001658362145015994",
            "extra": "mean: 106.5433723168279 usec\nrounds: 9038"
          }
        ]
      }
    ]
  }
}