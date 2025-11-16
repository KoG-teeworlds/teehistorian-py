# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-16

### Added
- Complete rewrite in Rust using PyO3 for better performance
- Type-safe chunk definitions
- Comprehensive error types: `ParseError`, `ValidationError`, `FileError`
- `TeehistorianParser` alias for backward compatibility
- Better validation for invalid teehistorian files
- Full type hints support

### Changed
- Improved API design with iterator pattern
- Enhanced error messages
- Better memory efficiency

### Fixed
- Memory leaks in chunk processing
- Edge cases in file parsing
- Unicode handling in strings

## [1.0.0] - Previous Release

### Added
- Initial Python implementation
- Basic teehistorian parsing
- Chunk type definitions
