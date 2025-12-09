#!/usr/bin/env python3
"""Analyze the header difference."""

import teehistorian_py as th
import json
from pathlib import Path

test_file = Path("tests/000c81cc-0922-4150-97e9-cd8f9776eb8e.teehistorian")

with open(test_file, "rb") as f:
    original_data = f.read()

# Parse
parser = th.Teehistorian(original_data)
header_bytes = parser.header()
header_json = json.loads(header_bytes.decode("utf-8"))

print("Original header JSON keys order:")
for key in header_json.keys():
    print(f"  - {key}")

print("\nOriginal header (first 200 chars):")
print(header_bytes[:200].decode("utf-8", errors="replace"))

# Now reconstruct
writer = th.TeehistorianWriter()
for key, value in header_json.items():
    if not key.startswith("__"):
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        writer.set_header(key, value_str)

# Get the new header
output_data = writer.getvalue()
# Extract header from output (16 bytes UUID + JSON + null)
uuid_size = 16
header_end = output_data.find(b'\x00', uuid_size)
new_header_bytes = output_data[uuid_size:header_end]

print("\nReconstructed header JSON keys order:")
new_header_json = json.loads(new_header_bytes.decode("utf-8"))
for key in new_header_json.keys():
    print(f"  - {key}")

print("\nReconstructed header (first 200 chars):")
print(new_header_bytes[:200].decode("utf-8", errors="replace"))

print("\nKey order matches:", list(header_json.keys()) == list(new_header_json.keys()))
print("Header content matches (ignoring order):", header_json == new_header_json)
