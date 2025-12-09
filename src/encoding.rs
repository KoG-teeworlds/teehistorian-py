///! Field encoding/decoding helpers for custom chunks
///!
///! This module provides utilities to encode and decode field values using
///! teehistorian-compatible formats (variable-width integers, length-prefixed strings, etc.)
use std::io::{self, Write};

/// Encode a variable-width integer (teehistorian format)
///
/// This uses the same variable-width encoding as teehistorian for consistency.
/// Positive values are encoded directly, negative values use zigzag encoding.
pub fn encode_varint(value: i32) -> Vec<u8> {
    let mut buf = Vec::new();
    encode_varint_into(&mut buf, value).unwrap();
    buf
}

/// Encode a variable-width integer into a writer
pub fn encode_varint_into<W: Write>(writer: &mut W, value: i32) -> io::Result<()> {
    // Zigzag encoding for signed integers
    let unsigned = ((value << 1) ^ (value >> 31)) as u32;

    let mut v = unsigned;
    loop {
        let mut byte = (v & 0x7F) as u8;
        v >>= 7;

        if v != 0 {
            byte |= 0x80; // Set continuation bit
        }

        writer.write_all(&[byte])?;

        if v == 0 {
            break;
        }
    }

    Ok(())
}

/// Decode a variable-width integer from bytes
///
/// Returns (value, bytes_consumed)
pub fn decode_varint(data: &[u8]) -> Result<(i32, usize), &'static str> {
    let mut result: u32 = 0;
    let mut shift = 0;
    let mut bytes_read = 0;

    for &byte in data {
        bytes_read += 1;

        result |= ((byte & 0x7F) as u32) << shift;

        if (byte & 0x80) == 0 {
            // Zigzag decode
            let value = ((result >> 1) as i32) ^ -((result & 1) as i32);
            return Ok((value, bytes_read));
        }

        shift += 7;

        if shift > 35 {
            return Err("Varint too long");
        }
    }

    Err("Incomplete varint")
}

/// Encode a fixed-width i8
pub fn encode_i8(value: i8) -> Vec<u8> {
    vec![value as u8]
}

/// Decode a fixed-width i8
pub fn decode_i8(data: &[u8]) -> Result<(i8, usize), &'static str> {
    if data.is_empty() {
        return Err("No data for i8");
    }
    Ok((data[0] as i8, 1))
}

/// Encode a fixed-width i16 (little-endian)
pub fn encode_i16(value: i16) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Decode a fixed-width i16 (little-endian)
pub fn decode_i16(data: &[u8]) -> Result<(i16, usize), &'static str> {
    if data.len() < 2 {
        return Err("Insufficient data for i16");
    }
    let bytes = [data[0], data[1]];
    Ok((i16::from_le_bytes(bytes), 2))
}

/// Encode a fixed-width i32 (little-endian)
pub fn encode_i32(value: i32) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Decode a fixed-width i32 (little-endian)
pub fn decode_i32(data: &[u8]) -> Result<(i32, usize), &'static str> {
    if data.len() < 4 {
        return Err("Insufficient data for i32");
    }
    let bytes = [data[0], data[1], data[2], data[3]];
    Ok((i32::from_le_bytes(bytes), 4))
}

/// Encode a fixed-width i64 (little-endian)
pub fn encode_i64(value: i64) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Decode a fixed-width i64 (little-endian)
pub fn decode_i64(data: &[u8]) -> Result<(i64, usize), &'static str> {
    if data.len() < 8 {
        return Err("Insufficient data for i64");
    }
    let bytes = [
        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
    ];
    Ok((i64::from_le_bytes(bytes), 8))
}

/// Encode a string (length-prefixed UTF-8)
///
/// Format: varint(length) + UTF-8 bytes
pub fn encode_string(value: &str) -> Vec<u8> {
    let bytes = value.as_bytes();
    let mut result = encode_varint(bytes.len() as i32);
    result.extend_from_slice(bytes);
    result
}

/// Decode a string (length-prefixed UTF-8)
///
/// Returns (string, bytes_consumed)
pub fn decode_string(data: &[u8]) -> Result<(String, usize), &'static str> {
    let (len, len_bytes) = decode_varint(data)?;

    if len < 0 {
        return Err("Negative string length");
    }

    let len = len as usize;
    let total_len = len_bytes + len;

    if data.len() < total_len {
        return Err("Insufficient data for string");
    }

    let string_bytes = &data[len_bytes..total_len];
    let string = String::from_utf8_lossy(string_bytes).to_string();

    Ok((string, total_len))
}

/// Encode raw bytes (length-prefixed)
///
/// Format: varint(length) + bytes
pub fn encode_bytes(value: &[u8]) -> Vec<u8> {
    let mut result = encode_varint(value.len() as i32);
    result.extend_from_slice(value);
    result
}

/// Decode raw bytes (length-prefixed)
///
/// Returns (bytes, bytes_consumed)
pub fn decode_bytes(data: &[u8]) -> Result<(Vec<u8>, usize), &'static str> {
    let (len, len_bytes) = decode_varint(data)?;

    if len < 0 {
        return Err("Negative bytes length");
    }

    let len = len as usize;
    let total_len = len_bytes + len;

    if data.len() < total_len {
        return Err("Insufficient data for bytes");
    }

    let bytes = data[len_bytes..total_len].to_vec();

    Ok((bytes, total_len))
}

/// Encode a UUID (16 bytes)
pub fn encode_uuid(value: &uuid::Uuid) -> Vec<u8> {
    value.as_bytes().to_vec()
}

/// Decode a UUID (16 bytes)
///
/// Returns (uuid, bytes_consumed)
pub fn decode_uuid(data: &[u8]) -> Result<(uuid::Uuid, usize), &'static str> {
    if data.len() < 16 {
        return Err("Insufficient data for UUID");
    }

    let uuid = uuid::Uuid::from_slice(&data[..16]).map_err(|_| "Invalid UUID bytes")?;

    Ok((uuid, 16))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_varint_roundtrip() {
        let test_values = vec![0, 1, -1, 127, -128, 1000, -1000, i32::MAX, i32::MIN];

        for value in test_values {
            let encoded = encode_varint(value);
            let (decoded, len) = decode_varint(&encoded).unwrap();
            assert_eq!(value, decoded);
            assert_eq!(len, encoded.len());
        }
    }

    #[test]
    fn test_string_roundtrip() {
        let test_strings = vec!["", "hello", "Hello, World!", "Üñíçödé"];

        for s in test_strings {
            let encoded = encode_string(s);
            let (decoded, len) = decode_string(&encoded).unwrap();
            assert_eq!(s, decoded);
            assert_eq!(len, encoded.len());
        }
    }

    #[test]
    fn test_bytes_roundtrip() {
        let test_bytes = vec![vec![], vec![0], vec![1, 2, 3, 4, 5], vec![255; 100]];

        for bytes in test_bytes {
            let encoded = encode_bytes(&bytes);
            let (decoded, len) = decode_bytes(&encoded).unwrap();
            assert_eq!(bytes, decoded);
            assert_eq!(len, encoded.len());
        }
    }

    #[test]
    fn test_fixed_width_integers() {
        // i8
        let (decoded, len) = decode_i8(&encode_i8(42)).unwrap();
        assert_eq!(42i8, decoded);
        assert_eq!(1, len);

        // i16
        let (decoded, len) = decode_i16(&encode_i16(1000)).unwrap();
        assert_eq!(1000i16, decoded);
        assert_eq!(2, len);

        // i32
        let (decoded, len) = decode_i32(&encode_i32(100000)).unwrap();
        assert_eq!(100000i32, decoded);
        assert_eq!(4, len);

        // i64
        let (decoded, len) = decode_i64(&encode_i64(10000000000i64)).unwrap();
        assert_eq!(10000000000i64, decoded);
        assert_eq!(8, len);
    }

    #[test]
    fn test_uuid_roundtrip() {
        // Use a fixed UUID for deterministic testing
        let uuid = uuid::Uuid::parse_str("550e8400-e29b-41d4-a716-446655440000").unwrap();
        let encoded = encode_uuid(&uuid);
        let (decoded, len) = decode_uuid(&encoded).unwrap();
        assert_eq!(uuid, decoded);
        assert_eq!(16, len);
    }
}
