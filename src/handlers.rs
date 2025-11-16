use std::borrow::Cow;
use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;
use teehistorian::Chunk;

use crate::chunks::*;
use crate::errors::{Result, TeehistorianParseError};

/// Handler for custom UUID chunks
#[derive(Debug, Clone)]
pub struct UuidHandler {
    uuid: String,
    name: String,
}

impl UuidHandler {
    pub fn new(uuid: String) -> Result<Self> {
        if uuid.is_empty() {
            return Err(TeehistorianParseError::Validation(
                "UUID cannot be empty".to_string(),
            ));
        }

        Ok(Self {
            name: uuid.clone(),
            uuid,
        })
    }

    /// Get the UUID string
    pub fn uuid(&self) -> &str {
        &self.uuid
    }

    /// Get the handler name
    pub fn name(&self) -> &str {
        &self.name
    }
}

/// Chunk converter that transforms Rust chunks to Python objects
pub struct ChunkConverter<'a> {
    handlers: &'a Arc<HashMap<String, UuidHandler>>,
}

impl<'a> ChunkConverter<'a> {
    /// Create a new chunk converter
    pub fn new(handlers: &'a Arc<HashMap<String, UuidHandler>>) -> Self {
        Self { handlers }
    }

    /// Convert a Rust chunk to a Python object
    pub fn convert(
        &self,
        py: Python<'_>,
        chunk: Chunk,
        _chunk_number: usize,
    ) -> PyResult<Py<PyAny>> {
        match chunk {
            // Player lifecycle events
            Chunk::Join { cid } => {
                let obj = PyJoin::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::JoinVer6 { cid } => {
                let obj = PyJoinVer6::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::Drop(drop_data) => {
                let reason = safe_decode(drop_data.reason);
                let obj = PyDrop::new(drop_data.cid, reason);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerReady { cid } => {
                let obj = PyPlayerReady::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            // Player state events
            Chunk::PlayerNew(p) => {
                let obj = PyPlayerNew::new(p.cid, p.x, p.y);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerOld { cid } => {
                let obj = PyPlayerOld::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerTeam { cid, team } => {
                let obj = PyPlayerTeam::new(cid, team);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerName(player_name) => {
                let name = safe_decode(player_name.name);
                let obj = PyPlayerName::new(player_name.cid, name);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerDiff(diff) => {
                let obj = PyPlayerDiff::new(diff.cid, diff.dx, diff.dy);
                Ok(Py::new(py, obj)?.into())
            }

            // Input events
            Chunk::InputNew(input_new) => {
                let input_str = format!("{:?}", input_new.input);
                let obj = PyInputNew::new(input_new.cid, input_str);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::InputDiff(diff) => {
                let input_vec = diff.dinput.to_vec();
                let obj = PyInputDiff::new(diff.cid, input_vec);
                Ok(Py::new(py, obj)?.into())
            }

            // Communication events
            Chunk::NetMessage(msg) => {
                let message = safe_decode(msg.msg);
                let obj = PyNetMessage::new(msg.cid, message);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::ConsoleCommand(console_cmd) => {
                let command = safe_decode(console_cmd.cmd);
                let args = console_cmd
                    .args
                    .iter()
                    .map(|arg| safe_decode(arg))
                    .collect::<Vec<_>>()
                    .join(" ");
                let obj = PyConsoleCommand::new(console_cmd.cid, console_cmd.flags, command, args);
                Ok(Py::new(py, obj)?.into())
            }

            // Authentication & version events
            Chunk::AuthLogin(auth) => {
                let auth_name = safe_decode(auth.auth_name);
                let obj = PyAuthLogin::new(auth.cid, auth.level, auth_name);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::DdnetVersion(ver) => {
                let connection_id = ver.connection_id.to_string();
                let version_str = ver.version_str.to_vec();
                let obj = PyDdnetVersion::new(ver.cid, connection_id, ver.version, version_str);
                Ok(Py::new(py, obj)?.into())
            }

            // Server events
            Chunk::TickSkip { dt } => {
                let obj = PyTickSkip::new(dt);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::TeamLoadSuccess(team_load) => {
                let save_str = format!("{:?}", team_load.save);
                let obj = PyTeamLoadSuccess::new(team_load.team, save_str);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::TeamLoadFailure { team } => {
                let obj = PyTeamLoadFailure::new(team);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::Antibot(data) => {
                let data_str = format!("{:?}", data);
                let obj = PyAntiBot::new(data_str);
                Ok(Py::new(py, obj)?.into())
            }

            // Special events
            Chunk::Eos => {
                let obj = PyEos::new();
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::UnknownEx(unknown_data) => {
                let uuid_str = unknown_data.uuid.to_string();
                let data = unknown_data.data.to_vec();

                // Check if we have a registered handler for this UUID
                if let Some(handler) = self.handlers.get(&uuid_str) {
                    let obj = PyCustomChunk::new(
                        handler.uuid().to_string(),
                        data,
                        handler.name().to_string(),
                    );
                    Ok(Py::new(py, obj)?.into())
                } else {
                    let obj = PyUnknown::new(uuid_str, data);
                    Ok(Py::new(py, obj)?.into())
                }
            }

            // Fallback for any unhandled chunk types
            _ => {
                let chunk_str = format!("{:?}", chunk);
                let obj = PyGeneric::new(chunk_str);
                Ok(Py::new(py, obj)?.into())
            }
        }
    }
}

/// Safely decode bytes to UTF-8 string with optimized allocation
///
/// This function attempts to decode bytes as UTF-8, falling back
/// to lossy conversion if strict decoding fails. It also strips
/// null bytes from the end of the string.
fn safe_decode(bytes: &[u8]) -> String {
    if bytes.is_empty() {
        return String::new();
    }

    // Try fast path for valid UTF-8 first
    match std::str::from_utf8(bytes) {
        Ok(s) => s.trim_end_matches('\0').to_string(),
        Err(_) => {
            // Fall back to lossy conversion only when needed
            let cow = String::from_utf8_lossy(bytes);
            match cow {
                Cow::Borrowed(s) => s.trim_end_matches('\0').to_string(),
                Cow::Owned(s) => s.trim_end_matches('\0').to_string(),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safe_decode() {
        // Valid UTF-8
        assert_eq!(safe_decode(b"hello"), "hello");

        // With null bytes
        assert_eq!(safe_decode(b"hello\0\0"), "hello");

        // Invalid UTF-8 (replaced with replacement character)
        let invalid = vec![0xFF, 0xFE];
        let decoded = safe_decode(&invalid);
        assert!(!decoded.is_empty());
    }

    #[test]
    fn test_uuid_handler() {
        // Valid handler
        let handler = UuidHandler::new("test-uuid".to_string());
        assert!(handler.is_ok());
        let handler = handler.unwrap();
        assert_eq!(handler.uuid(), "test-uuid");
        assert_eq!(handler.name(), "test-uuid");

        // Invalid handler (empty UUID)
        let handler = UuidHandler::new("".to_string());
        assert!(handler.is_err());
    }
}
