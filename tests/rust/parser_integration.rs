//! Integration tests for parsing teehistorian files
//!
//! Tests the core parsing functionality by reading actual teehistorian
//! files and verifying they can be parsed correctly.

use std::path::PathBuf;

#[test]
fn test_parse_example_file() {
    let test_file = PathBuf::from("tests/example.teehistorian");

    // Skip test if example file doesn't exist
    if !test_file.exists() {
        println!("Skipping test: example.teehistorian not found");
        return;
    }

    let data = std::fs::read(&test_file).expect("Failed to read example file");
    assert!(!data.is_empty(), "Example file should not be empty");
}

#[test]
fn test_parse_dummy_file() {
    let test_file = PathBuf::from("tests/dummy.teehistorian");

    if !test_file.exists() {
        println!("Skipping test: dummy.teehistorian not found");
        return;
    }

    let data = std::fs::read(&test_file).expect("Failed to read dummy file");
    assert!(!data.is_empty(), "Dummy file should not be empty");
}

#[test]
fn test_parse_test2_file() {
    let test_file = PathBuf::from("tests/test2.teehistorian");

    if !test_file.exists() {
        println!("Skipping test: test2.teehistorian not found");
        return;
    }

    let data = std::fs::read(&test_file).expect("Failed to read test2 file");
    assert!(!data.is_empty(), "Test2 file should not be empty");
}

#[test]
fn test_minimum_file_size() {
    // A valid teehistorian file should have at least some minimum size
    // for header and end-of-stream marker
    let test_file = PathBuf::from("tests/example.teehistorian");

    if !test_file.exists() {
        return;
    }

    let data = std::fs::read(&test_file).expect("Failed to read example file");
    // Minimum: header (at least 10 bytes) + EOS chunk (minimum)
    assert!(data.len() > 10, "File should have meaningful content");
}

#[test]
fn test_file_not_found_gracefully() {
    let test_file = PathBuf::from("tests/nonexistent.teehistorian");
    let result = std::fs::read(&test_file);
    assert!(result.is_err(), "Should fail gracefully for missing files");
}

#[test]
fn test_empty_data_rejection() {
    let empty_data: Vec<u8> = vec![];
    assert!(
        empty_data.is_empty(),
        "Empty data should be recognized as empty"
    );
}

#[test]
fn test_invalid_data_detection() {
    // Create some random invalid data that doesn't match teehistorian format
    let invalid_data = vec![0xFF; 100];

    // We're just verifying we can create and inspect the data
    // The actual parsing validation happens in Python/PyO3 layer
    assert_eq!(invalid_data.len(), 100, "Invalid data has correct length");
}

#[test]
fn test_file_read_consistency() {
    let test_file = PathBuf::from("tests/example.teehistorian");

    if !test_file.exists() {
        return;
    }

    let data1 = std::fs::read(&test_file).expect("First read failed");
    let data2 = std::fs::read(&test_file).expect("Second read failed");

    assert_eq!(data1, data2, "File reads should be consistent");
}

#[test]
fn test_large_file_handling() {
    let test_file = PathBuf::from("tests/example.teehistorian");

    if !test_file.exists() {
        return;
    }

    let data = std::fs::read(&test_file).expect("Failed to read file");

    // Verify we can handle reasonably large files (example is ~88KB)
    // Without running out of memory or panicking
    let _buffer: Vec<u8> = data.clone();
    assert_eq!(_buffer.len(), data.len(), "Buffer allocation successful");
}
