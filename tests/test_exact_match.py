#!/usr/bin/env python3
"""Test if reading and writing produces byte-for-byte identical files."""

import teehistorian_py as th
from pathlib import Path

# Test with the existing test file
test_file = Path("tests/000c81cc-0922-4150-97e9-cd8f9776eb8e.teehistorian")

if not test_file.exists():
    print(f"Test file not found: {test_file}")
    exit(1)

# Read original
with open(test_file, "rb") as f:
    original_data = f.read()

print(f"Original file size: {len(original_data):,} bytes")

# Parse
parser = th.Teehistorian(original_data)

# Get header
import json
header_json = json.loads(parser.header().decode("utf-8"))

# Create writer and copy header
writer = th.TeehistorianWriter()

# Copy all header fields
for key, value in header_json.items():
    if not key.startswith("__"):
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        writer.set_header(key, value_str)

# Write all chunks
chunk_count = 0
for chunk in parser:
    writer.write(chunk)
    chunk_count += 1

print(f"Wrote {chunk_count:,} chunks")

# Get output
output_data = writer.getvalue()
print(f"Output file size: {len(output_data):,} bytes")

# Compare
if original_data == output_data:
    print("✅ Files match byte-for-byte!")
else:
    print(f"❌ Files differ!")
    print(f"   Size difference: {len(output_data) - len(original_data):,} bytes")

    # Find first difference
    for i in range(min(len(original_data), len(output_data))):
        if original_data[i] != output_data[i]:
            print(f"   First difference at byte {i}")
            print(f"   Original: {original_data[max(0,i-10):i+10].hex()}")
            print(f"   Output:   {output_data[max(0,i-10):i+10].hex()}")
            break

    # Check if header differs
    # Headers end at first null byte after UUID (16 bytes)
    original_header_end = original_data.find(b'\x00', 16) + 1
    output_header_end = output_data.find(b'\x00', 16) + 1

    print(f"   Original header size: {original_header_end} bytes")
    print(f"   Output header size: {output_header_end} bytes")

    if original_data[:original_header_end] != output_data[:output_header_end]:
        print(f"   ❌ Headers differ!")
    else:
        print(f"   ✅ Headers match, chunks differ")
