use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use teehistorian::{Chunk, Th};

mod chunks;
mod errors;
mod handlers;

use chunks::*;
use errors::TeehistorianParseError;
use handlers::*;

/// Type alias for thread-safe handler storage
type HandlerMap = Arc<HashMap<String, UuidHandler>>;

/// Index-based parser structure
struct TeehistorianParserInner {
    data: Vec<u8>,
    parser: Option<Th<&'static [u8]>>,
}

impl TeehistorianParserInner {
    /// Create a new parser from data
    fn new(data: Vec<u8>) -> Result<Self, teehistorian::Error> {
        Ok(Self { data, parser: None })
    }

    /// Initialize parser lazily to avoid lifetime issues
    fn get_parser(&mut self) -> Result<&mut Th<&'static [u8]>, teehistorian::Error> {
        if self.parser.is_none() {
            let static_data: &'static [u8] = Box::leak(self.data.clone().into_boxed_slice());
            self.parser = Some(Th::parse(static_data)?);
        }
        Ok(self.parser.as_mut().unwrap())
    }

    /// Get the next chunk from the parser
    fn next_chunk(&mut self) -> Result<Option<Chunk<'_>>, teehistorian::Error> {
        let parser = self.get_parser()?;
        match parser.next_chunk() {
            Ok(chunk) => Ok(Some(chunk)),
            Err(e) if e.is_eof() => Ok(None),
            Err(e) => Err(e),
        }
    }

    /// Get header data
    fn header(&mut self) -> Result<Vec<u8>, teehistorian::Error> {
        let parser = self.get_parser()?;
        Ok(parser.header()?.to_vec())
    }
}

/// Main Teehistorian parser
///
/// This struct provides a safe, efficient interface for parsing
/// teehistorian files from Python
#[pyclass(name = "Teehistorian", module = "teehistorian_py")]
pub struct PyTeehistorian {
    inner: TeehistorianParserInner,
    handlers: HandlerMap,
    chunk_count: usize,
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
    fn new(data: &[u8]) -> PyResult<Self> {
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

        let mut parser = TeehistorianParserInner::new(data.to_vec()).map_err(|e| {
            TeehistorianParseError::Parse(format!("Failed to initialize parser: {}", e))
        })?;

        // Try to parse the header to validate the file format
        parser.header().map_err(|e| {
            TeehistorianParseError::Parse(format!("Invalid teehistorian file format: {}", e))
        })?;

        Ok(PyTeehistorian {
            inner: parser,
            handlers: Arc::new(HashMap::new()),
            chunk_count: 0,
        })
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

        // Use Arc::make_mut for efficient copy-on-write
        let handlers = Arc::make_mut(&mut self.handlers);
        handlers.insert(uuid_string, handler);

        Ok(())
    }

    /// Get the header data as bytes
    ///
    /// # Returns
    /// Header bytes or error
    fn header(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let header_bytes = self
            .inner
            .header()
            .map_err(|e| TeehistorianParseError::Header(e.to_string()))?;

        Ok(PyBytes::new(py, &header_bytes).into())
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
        match self.inner.next_chunk() {
            Ok(Some(chunk)) => {
                self.chunk_count += 1;
                let converter = ChunkConverter::new(&self.handlers);
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

/// Validate UUID string format
pub fn is_valid_uuid_format(uuid: &str) -> bool {
    let parts: Vec<&str> = uuid.split('-').collect();
    if parts.len() != 5 {
        return false;
    }

    let expected_lengths = [8, 4, 4, 4, 12];
    for (part, &expected_len) in parts.iter().zip(expected_lengths.iter()) {
        if part.len() != expected_len {
            return false;
        }

        if !part.chars().all(|c| c.is_ascii_hexdigit()) {
            return false;
        }
    }

    true
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
    m.add_class::<PyConsoleCommand>()?;

    // Add authentication and version chunks
    m.add_class::<PyAuthLogin>()?;
    m.add_class::<PyDdnetVersion>()?;

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
