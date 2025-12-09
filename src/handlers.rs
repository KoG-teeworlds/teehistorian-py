use std::cell::RefCell;
use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;
use teehistorian::Chunk;

use crate::chunks::*;
use crate::errors::{Result, TeehistorianParseError};
use crate::net_msg::{ClNetMessage, NetVersion, parse_net_msg};

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
    net_version: RefCell<NetVersion>,
}

impl<'a> ChunkConverter<'a> {
    /// Create a new chunk converter
    pub fn new(handlers: &'a Arc<HashMap<String, UuidHandler>>) -> Self {
        Self {
            handlers,
            net_version: RefCell::new(NetVersion::Unknown),
        }
    }

    /// Convert a Rust chunk to a Python object, preserving original serialized bytes
    pub fn convert(
        &self,
        py: Python<'_>,
        chunk: Chunk,
        _chunk_number: usize,
    ) -> PyResult<Py<PyAny>> {
        // Serialize the chunk immediately to preserve original bytes
        // This allows us to avoid re-serialization when writing unmodified chunks
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

            Chunk::JoinVer7 { cid } => {
                let obj = PyJoinVer7::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::RejoinVer6 { cid } => {
                let obj = PyRejoinVer6::new(cid);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::Drop(drop_data) => {
                let reason = String::from_utf8_lossy(drop_data.reason).to_string();
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
                let name = String::from_utf8_lossy(player_name.name)
                    .trim_end_matches('\0')
                    .to_string();
                let obj = PyPlayerName::new(player_name.cid, name);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::PlayerDiff(diff) => {
                let obj = PyPlayerDiff::new(diff.cid, diff.dx, diff.dy);
                Ok(Py::new(py, obj)?.into())
            }

            // Input events
            Chunk::InputNew(input_new) => {
                let input_vec = input_new.input.to_vec();
                let obj = PyInputNew::new(input_new.cid, input_vec);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::InputDiff(diff) => {
                let input_vec = diff.dinput.to_vec();
                let obj = PyInputDiff::new(diff.cid, input_vec);
                Ok(Py::new(py, obj)?.into())
            }

            // Communication events
            Chunk::NetMessage(msg) => {
                let message_bytes = msg.msg;

                // Try to parse the network message to extract player info
                let mut net_ver = self.net_version.borrow_mut();
                match parse_net_msg(message_bytes, &mut *net_ver) {
                    Ok(ClNetMessage::ClStartInfo(player_info)) => {
                        let name = String::from_utf8_lossy(player_info.name).to_string();
                        let clan = String::from_utf8_lossy(player_info.clan).to_string();

                        // Extract skin information including colors
                        let (skin_name, use_custom_color, color_body, color_feet) = match &player_info.skin {
                            crate::net_msg::Skin::V6(skin06) => (
                                String::from_utf8_lossy(skin06.skin).to_string(),
                                skin06.use_custom_color,
                                skin06.color_body,
                                skin06.color_feet,
                            ),
                            crate::net_msg::Skin::V7(_) => (
                                "default".to_string(),
                                false,
                                0,
                                0,
                            ),
                        };

                        let obj = PyNetMessagePlayerInfo::new(
                            msg.cid,
                            "ClStartInfo".to_string(),
                            name,
                            clan,
                            player_info.country,
                            skin_name,
                            use_custom_color,
                            color_body,
                            color_feet,
                        );
                        Ok(Py::new(py, obj)?.into())
                    }
                    Ok(ClNetMessage::ClChangeInfo(player_info)) => {
                        let name = String::from_utf8_lossy(player_info.name).to_string();
                        let clan = String::from_utf8_lossy(player_info.clan).to_string();

                        // Extract skin information including colors
                        let (skin_name, use_custom_color, color_body, color_feet) = match &player_info.skin {
                            crate::net_msg::Skin::V6(skin06) => (
                                String::from_utf8_lossy(skin06.skin).to_string(),
                                skin06.use_custom_color,
                                skin06.color_body,
                                skin06.color_feet,
                            ),
                            crate::net_msg::Skin::V7(_) => (
                                "default".to_string(),
                                false,
                                0,
                                0,
                            ),
                        };

                        let obj = PyNetMessagePlayerInfo::new(
                            msg.cid,
                            "ClChangeInfo".to_string(),
                            name,
                            clan,
                            player_info.country,
                            skin_name,
                            use_custom_color,
                            color_body,
                            color_feet,
                        );
                        Ok(Py::new(py, obj)?.into())
                    }
                    _ => {
                        // Fall back to regular NetMessage if parsing fails or it's not a player info message
                        let obj = PyNetMessage::new(msg.cid, message_bytes.to_vec());
                        Ok(Py::new(py, obj)?.into())
                    }
                }
            }

            Chunk::ConsoleCommand(console_cmd) => {
                let command = String::from_utf8_lossy(console_cmd.cmd).to_string();
                let args = console_cmd
                    .args
                    .iter()
                    .map(|arg| String::from_utf8_lossy(arg).to_string())
                    .collect::<Vec<_>>();
                let obj = PyConsoleCommand::new(console_cmd.cid, console_cmd.flags, command, args);
                Ok(Py::new(py, obj)?.into())
            }

            // Authentication & version events
            Chunk::AuthLogin(auth) => {
                let auth_name = String::from_utf8_lossy(auth.auth_name)
                    .trim_end_matches('\0')
                    .to_string();
                let obj = PyAuthLogin::new(auth.cid, auth.level, auth_name);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::DdnetVersion(ver) => {
                let connection_id = ver.connection_id.to_string();
                let version_str = ver.version_str.to_vec();
                let obj = PyDdnetVersion::new(ver.cid, connection_id, ver.version, version_str);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::DdnetVersionOld(ver) => {
                let obj = PyDdnetVersionOld::new(ver.cid, ver.version);
                Ok(Py::new(py, obj)?.into())
            }

            // Player events
            Chunk::PlayerFinish { cid, time } => {
                let obj = PyPlayerFinish::new(cid, time);
                Ok(Py::new(py, obj)?.into())
            }

            // Server events
            Chunk::TickSkip { dt } => {
                let obj = PyTickSkip::new(dt);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::TeamLoadSuccess(team_load) => {
                let save_id_str = team_load.save_id.to_string();
                let save_str = String::from_utf8_lossy(team_load.save)
                    .trim_end_matches('\0')
                    .to_string();
                let obj = PyTeamLoadSuccess::new(team_load.team, save_id_str, save_str);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::TeamLoadFailure { team } => {
                let obj = PyTeamLoadFailure::new(team);
                Ok(Py::new(py, obj)?.into())
            }

            Chunk::Antibot(data) => {
                // Convert bytes to String (lossy for non-UTF8)
                let data_str = String::from_utf8_lossy(data.data).to_string();
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
                // For unhandled chunks, create a Generic chunk with debug representation
                // This is a temporary fallback - ideally all chunks should have explicit handlers
                let chunk_str = format!("{:?}", chunk);
                eprintln!(
                    "Warning: Unhandled chunk type encountered: {}. Using Generic fallback. \
                     This chunk may not roundtrip correctly.",
                    chunk_str
                );
                let obj = PyGeneric::new(chunk_str);
                Ok(Py::new(py, obj)?.into())
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
