use std::collections::HashMap;

use ouroboros::self_referencing;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use teehistorian::{Chunk, Th};

mod chunks;
mod encoding;
mod errors;
mod handlers;
mod macros;
mod net_msg;
mod registry;
mod writer;

use chunks::*;
use errors::TeehistorianParseError;
use handlers::*;
use registry::{ChunkDef, FieldFormat, FieldSpec};
use writer::*;

const DEFAULT_MAX_INPUT_BYTES: usize = 1024 * 1024 * 1024;
const DEFAULT_MAX_HEADER_BYTES: usize = 16 * 1024 * 1024;
const DEFAULT_MAX_CHUNKS: usize = 100_000_000;
const DEFAULT_MAX_METADATA_CHUNKS: usize = 4_096;
const DEFAULT_MAX_FIELDS_PER_CHUNK: usize = 256;
const DEFAULT_MAX_NET_MESSAGE_BYTES: usize = 64 * 1024;

/// Safe self-referential parser using `ouroboros`
///
/// This structure safely holds data and a parser that references it, with zero
/// runtime overhead and no memory leaks. The `ouroboros` crate provides compile-time
/// guarantees that references remain valid.
#[self_referencing]
struct TeehistorianParserInner {
    data: Box<[u8]>,
    #[borrows(data)]
    #[covariant]
    parser: Th<&'this [u8]>,
}

impl TeehistorianParserInner {
    /// Create a new parser from data
    ///
    /// This is 100% safe with zero memory leaks and no unsafe code.
    fn from_data(data: Vec<u8>) -> Result<Self, teehistorian::Error> {
        let data_box = data.into_boxed_slice();

        // Try to build the self-referencing struct
        #[allow(clippy::borrowed_box)]
        {
            TeehistorianParserInnerTryBuilder {
                data: data_box,
                parser_builder: |data: &Box<[u8]>| Th::parse(data.as_ref()),
            }
            .try_build()
        }
    }

    /// Get the next chunk from the parser
    fn next_chunk(&mut self) -> Result<Option<Chunk<'_>>, teehistorian::Error> {
        self.with_parser_mut(|parser| match parser.next_chunk() {
            Ok(chunk) => Ok(Some(chunk)),
            Err(e) if e.is_eof() => Ok(None),
            Err(e) => Err(e),
        })
    }

    /// Get header data
    fn get_header(&mut self) -> Result<Vec<u8>, teehistorian::Error> {
        self.with_parser_mut(|parser| Ok(parser.header()?.to_vec()))
    }
}

/// Main Teehistorian parser
///
/// This struct provides a safe, efficient interface for parsing
/// teehistorian files from Python
#[pyclass(name = "Teehistorian", module = "teehistorian_py")]
pub struct PyTeehistorian {
    inner: TeehistorianParserInner,
    header: Box<[u8]>,
    handlers: HashMap<String, UuidHandler>,
    chunk_count: usize,
    net_version: net_msg::NetVersion,
    max_chunks: usize,
    max_metadata_chunks: usize,
    max_fields_per_chunk: usize,
    max_net_message_bytes: usize,
}

#[pymethods]
impl PyTeehistorian {
    /// Create a new Teehistorian parser from raw bytes
    ///
    /// # Arguments
    /// * `data` - Raw teehistorian file data
    ///
    /// # Returns
    /// A new parser instance or an error
    ///
    /// # Example
    /// ```python
    /// with open("demo.teehistorian", "rb") as f:
    ///     data = f.read()
    /// parser = Teehistorian(data)
    /// ```
    #[new]
    #[pyo3(signature = (
        data,
        *,
        max_input_bytes=DEFAULT_MAX_INPUT_BYTES,
        max_header_bytes=DEFAULT_MAX_HEADER_BYTES,
        max_chunks=DEFAULT_MAX_CHUNKS,
        max_metadata_chunks=DEFAULT_MAX_METADATA_CHUNKS,
        max_fields_per_chunk=DEFAULT_MAX_FIELDS_PER_CHUNK,
        max_net_message_bytes=DEFAULT_MAX_NET_MESSAGE_BYTES,
    ))]
    fn new(
        data: &[u8],
        max_input_bytes: usize,
        max_header_bytes: usize,
        max_chunks: usize,
        max_metadata_chunks: usize,
        max_fields_per_chunk: usize,
        max_net_message_bytes: usize,
    ) -> PyResult<Self> {
        for (name, value) in [
            ("max_input_bytes", max_input_bytes),
            ("max_header_bytes", max_header_bytes),
            ("max_chunks", max_chunks),
            ("max_metadata_chunks", max_metadata_chunks),
            ("max_fields_per_chunk", max_fields_per_chunk),
            ("max_net_message_bytes", max_net_message_bytes),
        ] {
            if value == 0 {
                return Err(TeehistorianParseError::Validation(format!(
                    "{name} must be greater than zero"
                ))
                .into());
            }
        }

        // Basic validation
        if data.is_empty() {
            return Err(
                TeehistorianParseError::Validation("Cannot parse empty data".to_string()).into(),
            );
        }

        // Validate minimum file size (teehistorian files have a header)
        if data.len() < 16 {
            return Err(TeehistorianParseError::Validation(
                "Data too short to be a valid teehistorian file".to_string(),
            )
            .into());
        }

        if data.len() > max_input_bytes {
            return Err(TeehistorianParseError::Validation(format!(
                "Input is {} bytes, exceeding max_input_bytes={max_input_bytes}",
                data.len()
            ))
            .into());
        }

        // The header begins after the 16-byte file UUID and ends at the first NUL.
        // Scan only the configured window so a missing terminator cannot turn this
        // validation into an unbounded operation.
        let after_magic = &data[16..];
        let scan_len = after_magic.len().min(max_header_bytes.saturating_add(1));
        match after_magic[..scan_len].iter().position(|byte| *byte == 0) {
            Some(header_len) => {
                debug_assert!(header_len <= max_header_bytes);
            }
            None if after_magic.len() > max_header_bytes => {
                return Err(TeehistorianParseError::Validation(format!(
                    "Header exceeds max_header_bytes={max_header_bytes}"
                ))
                .into());
            }
            None => {
                return Err(TeehistorianParseError::Validation(
                    "Truncated header: missing NUL terminator".to_string(),
                )
                .into());
            }
        }

        let mut parser = TeehistorianParserInner::from_data(data.to_vec()).map_err(|e| {
            TeehistorianParseError::Parse(format!("Failed to initialize parser: {}", e))
        })?;
        let header = parser
            .get_header()
            .map_err(|e| TeehistorianParseError::Header(format!("Failed to read header: {e}")))?
            .into_boxed_slice();

        let mut instance = PyTeehistorian {
            inner: parser,
            header,
            handlers: HashMap::new(),
            chunk_count: 0,
            net_version: net_msg::NetVersion::Unknown,
            max_chunks,
            max_metadata_chunks,
            max_fields_per_chunk,
            max_net_message_bytes,
        };

        // Parse header metadata and auto-register custom chunks
        instance.parse_and_register_metadata()?;

        Ok(instance)
    }

    /// Register a custom UUID handler
    ///
    /// # Arguments
    /// * `uuid_string` - The UUID string to register
    ///
    /// # Returns
    /// Ok(()) on success, error on failure
    fn register_custom_uuid(&mut self, uuid_string: String) -> PyResult<()> {
        // Basic validation only
        if uuid_string.is_empty() {
            return Err(TeehistorianParseError::Validation(
                "UUID string cannot be empty".to_string(),
            )
            .into());
        }

        // Validate UUID format
        if !is_valid_uuid_format(&uuid_string) {
            return Err(TeehistorianParseError::Validation(format!(
                "Invalid UUID format: {}",
                uuid_string
            ))
            .into());
        }

        // Create new handler
        let handler = UuidHandler::new(uuid_string.clone())
            .map_err(|e| TeehistorianParseError::Handler(e.to_string()))?;

        self.handlers.insert(uuid_string, handler);

        Ok(())
    }

    /// Get the header data as bytes
    ///
    /// # Returns
    /// Header bytes or error
    fn header(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(PyBytes::new(py, &self.header).into())
    }

    /// Get the header data as a JSON string
    ///
    /// # Returns
    /// Header as JSON string or error
    fn get_header_str(&self) -> PyResult<String> {
        // Parse the header to extract the JSON string
        // The teehistorian header format is: [JSON header][null terminator][chunks...]
        let header_str = std::str::from_utf8(&self.header).map_err(|e| {
            TeehistorianParseError::Header(format!("Invalid UTF-8 in header: {}", e))
        })?;

        Ok(header_str.to_owned())
    }

    /// Python iterator protocol support
    fn __iter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    /// Get the next chunk from the parser
    ///
    /// # Returns
    /// Next chunk as Python object or None at EOF
    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if self.chunk_count >= self.max_chunks {
            return Err(TeehistorianParseError::Validation(format!(
                "Chunk limit exceeded: max_chunks={}",
                self.max_chunks
            ))
            .into());
        }

        match self.inner.next_chunk() {
            Ok(Some(chunk)) => {
                self.chunk_count += 1;
                let mut converter = ChunkConverter::new(
                    &self.handlers,
                    &mut self.net_version,
                    self.max_net_message_bytes,
                );
                let py_chunk = converter.convert(py, chunk, self.chunk_count)?;
                Ok(Some(py_chunk))
            }
            Ok(None) => Ok(None),
            Err(e) => Err(TeehistorianParseError::Parse(format!(
                "Failed to parse chunk {}: {}",
                self.chunk_count, e
            ))
            .into()),
        }
    }

    /// Get the next chunk from the parser (for backward compatibility)
    ///
    /// This method provides a convenient way to manually iterate through chunks
    /// without using Python's iterator protocol.
    ///
    /// # Returns
    /// Next chunk as Python object or None at EOF
    fn next_chunk(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        self.__next__(py)
    }

    /// Get the current chunk count
    #[getter]
    fn chunk_count(&self) -> usize {
        self.chunk_count
    }

    /// Get registered handler UUIDs
    fn get_registered_uuids(&self) -> Vec<String> {
        self.handlers.keys().cloned().collect()
    }

    /// Context manager entry
    fn __enter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    /// Context manager exit
    fn __exit__(
        &mut self,
        _exc_type: Option<&Bound<'_, pyo3::types::PyAny>>,
        _exc_value: Option<&Bound<'_, pyo3::types::PyAny>>,
        _traceback: Option<&Bound<'_, pyo3::types::PyAny>>,
    ) -> PyResult<bool> {
        // Nothing to clean up, just return False to not suppress exceptions
        Ok(false)
    }
}

impl PyTeehistorian {
    /// Parse header metadata and auto-register custom chunks
    ///
    /// This method looks for __teehistorian_py metadata in the file header
    /// and automatically registers any custom chunk definitions found.
    fn parse_and_register_metadata(&mut self) -> PyResult<()> {
        // Parse as JSON
        let header_json: serde_json::Value = serde_json::from_slice(&self.header).map_err(|e| {
            TeehistorianParseError::Header(format!("Failed to parse header JSON: {}", e))
        })?;

        // Check for __teehistorian_py metadata
        if let Some(metadata) = header_json.get("__teehistorian_py")
            && let Some(chunks) = metadata.get("chunks")
            && let Some(chunks_obj) = chunks.as_object()
        {
            if chunks_obj.len() > self.max_metadata_chunks {
                return Err(TeehistorianParseError::Validation(format!(
                    "Metadata defines {} chunks, exceeding max_metadata_chunks={}",
                    chunks_obj.len(),
                    self.max_metadata_chunks
                ))
                .into());
            }

            // Fully validate all untrusted metadata before modifying either the
            // process-global registry or this parser's handler map.
            let mut definitions = Vec::with_capacity(chunks_obj.len());
            for (uuid, chunk_data) in chunks_obj {
                if let Some(chunk_obj) = chunk_data.as_object() {
                    if !is_valid_uuid_format(uuid) {
                        return Err(TeehistorianParseError::Validation(format!(
                            "Invalid metadata UUID format: {uuid}"
                        ))
                        .into());
                    }

                    // Extract chunk name
                    let chunk_name = chunk_obj
                        .get("name")
                        .and_then(|v| v.as_str())
                        .unwrap_or("UnknownChunk")
                        .to_string();

                    // Extract fields
                    let mut fields = Vec::new();
                    if let Some(fields_obj) = chunk_obj.get("fields").and_then(|v| v.as_object()) {
                        if fields_obj.len() > self.max_fields_per_chunk {
                            return Err(TeehistorianParseError::Validation(format!(
                                "Metadata chunk {uuid} defines {} fields, exceeding max_fields_per_chunk={}",
                                fields_obj.len(),
                                self.max_fields_per_chunk
                            ))
                            .into());
                        }
                        for (field_name, field_data) in fields_obj {
                            if let Some(field_obj) = field_data.as_object() {
                                // Parse format string back to enum
                                let format_str = field_obj
                                    .get("format")
                                    .and_then(|v| v.as_str())
                                    .unwrap_or("Varint");

                                let field_format = match format_str {
                                    "I8" => registry::FieldFormat::I8,
                                    "I16" => registry::FieldFormat::I16,
                                    "I32" => registry::FieldFormat::I32,
                                    "I64" => registry::FieldFormat::I64,
                                    "String" => registry::FieldFormat::String,
                                    "Bytes" => registry::FieldFormat::Bytes,
                                    "Uuid" => registry::FieldFormat::Uuid,
                                    _ => registry::FieldFormat::Varint,
                                };

                                fields.push(registry::FieldSpec {
                                    name: field_name.clone(),
                                    format: field_format,
                                    description: None,
                                });
                            }
                        }
                    }

                    // Create chunk definition
                    let chunk_def = registry::ChunkDef {
                        uuid: uuid.clone(),
                        name: chunk_name,
                        fields,
                    };

                    let handler = UuidHandler::new(uuid.clone())
                        .map_err(|e| TeehistorianParseError::Handler(e.to_string()))?;
                    definitions.push((chunk_def, handler));
                }
            }

            for (chunk_def, handler) in definitions {
                registry::register_global(chunk_def.clone());
                self.handlers.insert(chunk_def.uuid, handler);
            }
        }

        Ok(())
    }
}

/// Validate UUID string format
pub fn is_valid_uuid_format(uuid: &str) -> bool {
    uuid::Uuid::parse_str(uuid).is_ok()
}

/// Python module definition
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add(
        "__doc__",
        "High-performance Teehistorian parser written in Rust",
    )?;

    // Add exception types
    m.add(
        "TeehistorianError",
        m.py().get_type::<errors::TeehistorianError>(),
    )?;
    m.add("ParseError", m.py().get_type::<errors::ParseError>())?;
    m.add(
        "ValidationError",
        m.py().get_type::<errors::ValidationError>(),
    )?;
    m.add("FileError", m.py().get_type::<errors::FileError>())?;
    m.add("WriteError", m.py().get_type::<errors::WriteError>())?;

    // Add main parser class
    m.add_class::<PyTeehistorian>()?;

    // Add player lifecycle chunks
    m.add_class::<PyJoin>()?;
    m.add_class::<PyJoinVer6>()?;
    m.add_class::<PyDrop>()?;
    m.add_class::<PyPlayerReady>()?;

    // Add player state chunks
    m.add_class::<PyPlayerNew>()?;
    m.add_class::<PyPlayerOld>()?;
    m.add_class::<PyPlayerTeam>()?;
    m.add_class::<PyPlayerName>()?;
    m.add_class::<PyPlayerDiff>()?;

    // Add input chunks
    m.add_class::<PyInputNew>()?;
    m.add_class::<PyInputDiff>()?;

    // Add communication chunks
    m.add_class::<PyNetMessage>()?;
    m.add_class::<PyNetMessagePlayerInfo>()?;
    m.add_class::<PyConsoleCommand>()?;

    // Add authentication and version chunks
    m.add_class::<PyAuthLogin>()?;
    m.add_class::<PyDdnetVersion>()?;
    m.add_class::<PyDdnetVersionOld>()?;
    m.add_class::<PyPlayerFinish>()?;

    // Add server event chunks
    m.add_class::<PyTickSkip>()?;
    m.add_class::<PyTeamLoadSuccess>()?;
    m.add_class::<PyTeamLoadFailure>()?;
    m.add_class::<PyAntiBot>()?;

    // Add special chunks
    m.add_class::<PyEos>()?;
    m.add_class::<PyUnknown>()?;
    m.add_class::<PyCustomChunk>()?;
    m.add_class::<PyGeneric>()?;

    // Add writer class (at end to debug export issue)
    m.add_class::<PyTeehistorianWriter>()?;

    // Add registry classes and functions
    m.add_class::<FieldFormat>()?;
    m.add_class::<FieldSpec>()?;
    m.add_class::<ChunkDef>()?;
    m.add_function(wrap_pyfunction!(
        registry::py_api::register_global_chunk,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        registry::py_api::unregister_global_chunk,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(registry::py_api::get_global_chunk, m)?)?;
    m.add_function(wrap_pyfunction!(registry::py_api::list_global_chunks, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_uuid_format() {
        assert!(is_valid_uuid_format("12345678-1234-5678-1234-567812345678"));
        assert!(!is_valid_uuid_format("invalid-uuid"));
        assert!(!is_valid_uuid_format("12345678-1234-5678-1234"));
        assert!(!is_valid_uuid_format(
            "12345678-1234-5678-1234-56781234567g"
        )); // 'g' is not hex
    }
}
