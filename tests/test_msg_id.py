#!/usr/bin/env python3
"""Test message ID encoding."""

# Decode varint
def decode_varint(byte_val):
    """Decode single byte varint (for small values)."""
    # Zigzag decoding
    unsigned = byte_val
    signed = (unsigned >> 1) ^ -(unsigned & 1)
    return signed

# Test both values
our_val = 0x01
original_val = 0x28

print(f"Our encoding:      0x{our_val:02x} = {our_val} decimal")
print(f"  Zigzag decoded:  {decode_varint(our_val)}")

print(f"\nOriginal encoding: 0x{original_val:02x} = {original_val} decimal")
print(f"  Zigzag decoded:  {decode_varint(original_val)}")

# The pattern:
# 0x01 >> 1 = 0, so our value = 0
# 0x28 >> 1 = 0x14 = 20, so original value = 20

print("\n" + "="*60)
print("HYPOTHESIS:")
print("="*60)
print("""
It looks like the message ID for ClStartInfo might be 20, not 1!

Let me check the DDNet protocol documentation...

Actually, looking at the tw2 protocol, there might be different
message ID mappings for different game versions or protocols.

The libtw2_gamenet_ddnet crate might use message ID 1 internally,
but the wire format uses a different ID (20).
""")
