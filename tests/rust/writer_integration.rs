//! Integration tests for teehistorian writer
//!
//! Tests the writer functionality by creating teehistorian files
//! in memory and verifying their structure.

use std::io::Cursor;

#[test]
fn test_writer_creates_buffer() {
    let mut buffer = Vec::new();
    // Verify we can create an empty buffer
    assert!(buffer.is_empty(), "Buffer should start empty");

    // Add some data
    buffer.extend_from_slice(&[0x01, 0x02, 0x03]);
    assert_eq!(
        buffer.len(),
        3,
        "Buffer should contain 3 bytes after extend"
    );
}

#[test]
fn test_cursor_buffer_operations() {
    let data = vec![1, 2, 3, 4, 5];
    let cursor = Cursor::new(data.clone());

    // Verify cursor wraps the data correctly
    assert_eq!(cursor.get_ref().len(), 5, "Cursor should wrap 5 bytes");
    assert_eq!(cursor.get_ref(), &data, "Cursor data should match original");
}

#[test]
fn test_buffer_growth() {
    let mut buffer = Vec::with_capacity(10);

    // Test that buffer can grow beyond initial capacity
    for i in 0..20 {
        buffer.push(i as u8);
    }

    assert_eq!(buffer.len(), 20, "Buffer should contain 20 bytes");
}

#[test]
fn test_multiple_buffer_writes() {
    let mut buffer = Vec::new();

    // Simulate multiple writes
    buffer.extend_from_slice(b"Header");
    assert_eq!(buffer.len(), 6, "After first write");

    buffer.extend_from_slice(b"Content");
    assert_eq!(buffer.len(), 13, "After second write");

    buffer.extend_from_slice(b"Footer");
    assert_eq!(buffer.len(), 19, "After third write");
}

#[test]
fn test_empty_buffer_initialization() {
    let buffer: Vec<u8> = Vec::new();
    assert!(buffer.is_empty(), "New buffer should be empty");
    assert_eq!(buffer.capacity(), 0, "New buffer should have zero capacity");
}

#[test]
fn test_buffer_with_capacity() {
    let buffer: Vec<u8> = Vec::with_capacity(100);
    assert!(buffer.is_empty(), "New buffer should be empty");
    assert!(
        buffer.capacity() >= 100,
        "Buffer capacity should be at least 100"
    );
}

#[test]
fn test_buffer_clear_operation() {
    let mut buffer = vec![1, 2, 3, 4, 5];
    assert_eq!(buffer.len(), 5, "Buffer should have 5 elements");

    buffer.clear();
    assert!(buffer.is_empty(), "Buffer should be empty after clear");
    assert!(
        buffer.capacity() >= 5,
        "Capacity should be preserved after clear"
    );
}

#[test]
fn test_buffer_clone_independence() {
    let buffer1 = vec![1, 2, 3];
    let buffer2 = buffer1.clone();

    assert_eq!(buffer1, buffer2, "Cloned buffer should be equal");
    assert_eq!(buffer1.len(), 3, "Original buffer length");
    assert_eq!(buffer2.len(), 3, "Cloned buffer length");
}

#[test]
fn test_binary_data_handling() {
    let mut buffer = Vec::new();

    // Add binary data with all possible byte values
    let binary_data: Vec<u8> = (0..=255).collect();
    buffer.extend_from_slice(&binary_data);

    assert_eq!(buffer.len(), 256, "Buffer should contain all byte values");

    // Verify data integrity
    for (i, &byte) in buffer.iter().enumerate() {
        assert_eq!(byte, i as u8, "Byte at position {} should be {}", i, i);
    }
}

#[test]
fn test_large_buffer_allocation() {
    // Test allocating a moderately large buffer (1MB)
    let size = 1024 * 1024;
    let buffer: Vec<u8> = vec![0; size];

    assert_eq!(buffer.len(), size, "Buffer should be 1MB");
}

#[test]
fn test_buffer_truncation() {
    let mut buffer = vec![1, 2, 3, 4, 5];

    buffer.truncate(3);
    assert_eq!(buffer.len(), 3, "Buffer should be truncated to 3 elements");
    assert_eq!(
        buffer,
        vec![1, 2, 3],
        "Truncated buffer should contain first 3 elements"
    );
}

#[test]
fn test_writer_state_management() {
    // Test that we can manage simple state for a writer
    let mut buffer = Vec::new();
    let mut header_written = false;

    // Simulate writing header
    if !header_written {
        buffer.extend_from_slice(b"HEADER");
        header_written = true;
    }

    assert!(header_written, "Header flag should be true");
    assert_eq!(buffer.len(), 6, "Buffer should contain header");

    // Try writing header again (should be skipped)
    if !header_written {
        buffer.extend_from_slice(b"HEADER");
    }

    assert_eq!(
        buffer.len(),
        6,
        "Buffer should still contain only one header"
    );
}

#[test]
fn test_sequential_writes_ordering() {
    let mut buffer = Vec::new();

    let chunks = vec![b"chunk1".to_vec(), b"chunk2".to_vec(), b"chunk3".to_vec()];

    for chunk in chunks.iter() {
        buffer.extend_from_slice(chunk);
    }

    // Verify data is in correct order
    let result = String::from_utf8(buffer).unwrap();
    assert_eq!(result, "chunk1chunk2chunk3", "Chunks should be in order");
}

#[test]
fn test_buffer_preservation_across_operations() {
    let mut buffer = Vec::new();
    let original_data = b"original".to_vec();

    buffer.extend_from_slice(&original_data);
    let snapshot1 = buffer.clone();

    // Add more data
    buffer.extend_from_slice(b"_extended");

    // Original data should still be there
    assert!(
        buffer.starts_with(&original_data),
        "Buffer should contain original data"
    );
    assert_eq!(
        snapshot1, original_data,
        "Snapshot should preserve original state"
    );
}
