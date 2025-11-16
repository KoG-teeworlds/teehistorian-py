use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use thiserror::Error;

create_exception!(
    teehistorian_py,
    TeehistorianError,
    PyException,
    "Base exception for all teehistorian parsing errors"
);

create_exception!(
    teehistorian_py,
    ParseError,
    TeehistorianError,
    "Exception for parsing errors"
);

create_exception!(
    teehistorian_py,
    ValidationError,
    TeehistorianError,
    "Exception for validation errors"
);

create_exception!(
    teehistorian_py,
    FileError,
    TeehistorianError,
    "Exception for file I/O errors"
);

/// Error enum for all possible errors in the library
#[derive(Debug, Error)]
pub enum TeehistorianParseError {
    /// Initialization errors
    #[error("Initialization failed: {0}")]
    Initialization(String),

    /// Header parsing errors
    #[error("Header parsing failed: {0}")]
    Header(String),

    /// General parsing errors
    #[error("Parse error: {0}")]
    Parse(String),

    /// Validation errors
    #[error("Validation failed: {0}")]
    Validation(String),

    /// Handler-related errors
    #[error("Handler error: {0}")]
    Handler(String),

    /// IO errors
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    /// UTF-8 decoding errors
    #[error("UTF-8 decode error: {0}")]
    Utf8(#[from] std::string::FromUtf8Error),

    /// End of file reached (not really an error)
    #[error("End of file reached")]
    Eof,
}

impl From<TeehistorianParseError> for PyErr {
    fn from(err: TeehistorianParseError) -> Self {
        match err {
            TeehistorianParseError::Eof => {
                // EOF is expected, convert to StopIteration for Python
                pyo3::exceptions::PyStopIteration::new_err(err.to_string())
            }
            TeehistorianParseError::Parse(_) | TeehistorianParseError::Header(_) => {
                ParseError::new_err(err.to_string())
            }
            TeehistorianParseError::Validation(_) => ValidationError::new_err(err.to_string()),
            TeehistorianParseError::Io(_) => FileError::new_err(err.to_string()),
            _ => {
                // All other errors become base TeehistorianError exceptions
                TeehistorianError::new_err(err.to_string())
            }
        }
    }
}

/// Result type alias for convenience
pub type Result<T> = std::result::Result<T, TeehistorianParseError>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_conversion() {
        let err = TeehistorianParseError::Validation("Invalid data".to_string());
        let py_err: PyErr = err.into();
        assert!(
            py_err
                .to_string()
                .contains("Validation failed: Invalid data")
        );
    }
}
