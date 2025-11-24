use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::any::type_name;
use std::io::Cursor;
use teehistorian::Chunk;

// Import macros from the macros module
use crate::{define_chunk, define_chunk_custom, define_inline_chunk, define_zero_field_chunk};

/// Base trait for all chunk types that can be written to teehistorian format
pub trait TeehistorianChunk {
    /// Convert this chunk to the corresponding teehistorian::Chunk enum variant
    fn to_teehistorian_chunk(&self) -> Chunk<'_>;

    /// Get the chunk type name from Rust type
    fn chunk_type(&self) -> &'static str {
        // Extract just the struct name without the "Py" prefix and module path
        let full_name = type_name::<Self>();
        full_name
            .split("::")
            .last()
            .unwrap_or(full_name)
            .strip_prefix("Py")
            .unwrap_or(full_name)
    }

    /// Serialize this chunk to bytes
    fn write_to_buffer(&self) -> PyResult<Vec<u8>> {
        let chunk = self.to_teehistorian_chunk();
        let mut cursor = Cursor::new(Vec::new());
        teehistorian::serialize_into(&mut cursor, &chunk).map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to serialize chunk: {}",
                e
            ))
        })?;
        Ok(cursor.into_inner())
    }
}

/// Generic Python methods implementation for all chunks
pub trait PyChunkMethods: TeehistorianChunk + std::fmt::Debug {
    fn py_write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let bytes = self.write_to_buffer()?;
        Ok(PyBytes::new(py, &bytes).into())
    }

    fn py_repr(&self) -> String {
        format!("{:?}", self)
    }

    fn py_chunk_type(&self) -> &'static str {
        self.chunk_type()
    }
}

// Blanket implementation for all types that implement TeehistorianChunk + Debug
impl<T> PyChunkMethods for T where T: TeehistorianChunk + std::fmt::Debug {}

// ============================================================================
// CHUNK DEFINITIONS USING MACROS
// ============================================================================

// Player Lifecycle Chunks
// ----------------------------------------------------------------------------

define_inline_chunk! {
    /// Player joins the server
    Join {
        client_id: i32 => cid,
    }
}

define_inline_chunk! {
    /// Player joins with version 6 protocol
    JoinVer6 {
        client_id: i32 => cid,
    }
}

define_chunk! {
    /// Player disconnects from server
    Drop(Drop) {
        client_id: i32 => cid,
        reason: String => reason,
    }
}

// PlayerReady doesn't have a struct in teehistorian 0.12, it's just { cid }
// We need to handle it manually in handlers.rs, or use a workaround
// For now, create a simple struct that matches the inline variant
/// Player becomes ready to play
/// Category: PlayerLifecycle
#[pyclass(module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyPlayerReady {
    #[pyo3(get)]
    pub client_id: i32,
}

impl PyPlayerReady {
    pub fn new(client_id: i32) -> Self {
        Self { client_id }
    }
}

impl TeehistorianChunk for PyPlayerReady {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        // PlayerReady is represented as PlayerName with empty name in teehistorian 0.12
        Chunk::PlayerName(teehistorian::chunks::PlayerName {
            cid: self.client_id,
            name: b"",
        })
    }
}

#[pymethods]
impl PyPlayerReady {
    #[new]
    fn py_new(client_id: i32) -> Self {
        Self::new(client_id)
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self)
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        "PlayerReady"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("client_id", self.client_id)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }
}

// Player State Chunks
// ----------------------------------------------------------------------------

define_chunk! {
    /// New player spawn position
    PlayerNew(PlayerNew) {
        client_id: i32 => cid,
        x: i32 => x,
        y: i32 => y,
    }
}

define_inline_chunk! {
    /// Player leaves game (but not server)
    PlayerOld {
        client_id: i32 => cid,
    }
}

// PlayerTeam is an inline variant { cid, team } in teehistorian 0.12
/// Player changes team
/// Category: PlayerState
#[pyclass(module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyPlayerTeam {
    #[pyo3(get)]
    pub client_id: i32,
    #[pyo3(get)]
    pub team: i32,
}

impl PyPlayerTeam {
    pub fn new(client_id: i32, team: i32) -> Self {
        Self { client_id, team }
    }
}

impl TeehistorianChunk for PyPlayerTeam {
    fn to_teehistorian_chunk(&self) -> Chunk<'static> {
        // PlayerTeam doesn't have a direct teehistorian representation
        // Use PlayerName with empty name as fallback
        Chunk::PlayerName(teehistorian::chunks::PlayerName {
            cid: self.client_id,
            name: b"",
        })
    }
}

#[pymethods]
impl PyPlayerTeam {
    #[new]
    fn py_new(client_id: i32, team: i32) -> Self {
        Self::new(client_id, team)
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self)
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        "PlayerTeam"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("client_id", self.client_id)?;
        dict.set_item("team", self.team)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }
}

define_chunk_custom! {
    /// Player changes name
    PlayerName(PlayerName) {
        client_id: i32 => cid,
        name: String => name [as_bytes],
    }
}

define_chunk! {
    /// Player position difference/update
    PlayerDiff(PlayerDiff) {
        client_id: i32 => cid,
        dx: i32 => dx,
        dy: i32 => dy,
    }
}

// Input Chunks - These have fixed-size arrays [i32; 10]
// ----------------------------------------------------------------------------

/// New player input state
/// Category: Input
#[pyclass(module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyInputNew {
    #[pyo3(get)]
    pub client_id: i32,
    #[pyo3(get)]
    pub input: Vec<i32>,
}

impl PyInputNew {
    pub fn new(client_id: i32, input: Vec<i32>) -> Self {
        Self { client_id, input }
    }
}

impl TeehistorianChunk for PyInputNew {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        let mut input_array = [0i32; 10];
        for (i, &val) in self.input.iter().take(10).enumerate() {
            input_array[i] = val;
        }
        Chunk::InputNew(teehistorian::chunks::InputNew {
            cid: self.client_id,
            input: input_array,
        })
    }
}

#[pymethods]
impl PyInputNew {
    #[new]
    fn py_new(client_id: i32, input: Vec<i32>) -> Self {
        Self::new(client_id, input)
    }

    fn __repr__(&self) -> String {
        self.py_repr()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        self.py_chunk_type()
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("client_id", self.client_id)?;
        dict.set_item("input", &self.input)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }
}

/// Player input difference from previous state
/// Category: Input
#[pyclass(module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyInputDiff {
    #[pyo3(get)]
    pub client_id: i32,
    #[pyo3(get)]
    pub input: Vec<i32>,
}

impl PyInputDiff {
    pub fn new(client_id: i32, input: Vec<i32>) -> Self {
        Self { client_id, input }
    }
}

impl TeehistorianChunk for PyInputDiff {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        let mut dinput_array = [0i32; 10];
        for (i, &val) in self.input.iter().take(10).enumerate() {
            dinput_array[i] = val;
        }
        Chunk::InputDiff(teehistorian::chunks::InputDiff {
            cid: self.client_id,
            dinput: dinput_array,
        })
    }
}

#[pymethods]
impl PyInputDiff {
    #[new]
    fn py_new(client_id: i32, input: Vec<i32>) -> Self {
        Self::new(client_id, input)
    }

    fn __repr__(&self) -> String {
        self.py_repr()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        self.py_chunk_type()
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("client_id", self.client_id)?;
        dict.set_item("input", &self.input)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }
}

// Communication Chunks
// ----------------------------------------------------------------------------

define_chunk_custom! {
    /// Network message from/to player
    NetMessage(NetMessage) {
        client_id: i32 => cid,
        msg: String => msg [as_bytes],
    }
}

define_chunk_custom! {
    /// Console command executed by player
    ConsoleCommand(ConsoleCommand) {
        client_id: i32 => cid,
        flags: i32 => flags,
        cmd: String => cmd [as_bytes],
        args: String => args [as_args_vec],
    }
}

// Authentication & Version Chunks
// ----------------------------------------------------------------------------

define_chunk_custom! {
    /// Player authentication/login
    AuthLogin(AuthLogin::Auth) {
        client_id: i32 => cid,
        level: i32 => level,
        auth_name: String => auth_name [as_bytes],
    }
}

define_chunk_custom! {
    /// DDNet client version information
    DdnetVersion(DdnetVersion) {
        client_id: i32 => cid,
        connection_id: String => connection_id [as_uuid],
        version: i32 => version,
        version_str: Vec<u8> => version_str [as_slice],
    }
}

// Server Event Chunks
// ----------------------------------------------------------------------------

define_inline_chunk! {
    /// Server tick skip (time advancement)
    TickSkip {
        dt: i32 => dt,
    }
}

define_chunk_custom! {
    /// Team save loaded successfully
    TeamLoadSuccess(TeamLoadSuccess::TeamSave) {
        team: i32 => team,
        save_id: String => save_id [as_uuid],
        save: String => save [as_bytes],
    }
}

define_inline_chunk! {
    /// Team save load failed
    TeamLoadFailure {
        team: i32 => team,
    }
}

define_chunk_custom! {
    /// Anti-bot system event
    AntiBot(Antibot) {
        data: String => data [as_bytes],
    }
}

// Special Chunks
// ----------------------------------------------------------------------------

define_zero_field_chunk! {
    /// End of stream marker
    Eos(Eos)
}

// ----------------------------------------------------------------------------
// Special Chunks with Custom Implementations
// ----------------------------------------------------------------------------

/// Unknown chunk with UUID (not registered)
#[pyclass(name = "Unknown", module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyUnknown {
    #[pyo3(get)]
    pub uuid: String,
    #[pyo3(get)]
    pub data: Vec<u8>,
}

impl PyUnknown {
    pub fn new(uuid: String, data: Vec<u8>) -> Self {
        Self { uuid, data }
    }
}

impl TeehistorianChunk for PyUnknown {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        // Parse UUID string to uuid::Uuid
        let uuid_parsed = uuid::Uuid::parse_str(&self.uuid).unwrap_or_default();

        Chunk::UnknownEx(teehistorian::chunks::UnknownEx {
            uuid: uuid_parsed,
            data: &self.data,
        })
    }
}

#[pymethods]
impl PyUnknown {
    #[new]
    fn py_new(uuid: String, data: Vec<u8>) -> Self {
        Self::new(uuid, data)
    }

    fn __repr__(&self) -> String {
        self.py_repr()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        self.py_chunk_type()
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("uuid", &self.uuid)?;
        dict.set_item("data", &self.data)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }

    fn data_preview(&self) -> String {
        let preview_len = self.data.len().min(32);
        let hex: String = self.data[..preview_len]
            .iter()
            .map(|b| format!("{:02x}", b))
            .collect::<Vec<_>>()
            .join(" ");
        if self.data.len() > 32 {
            format!("{}... ({} bytes total)", hex, self.data.len())
        } else {
            format!("{} ({} bytes)", hex, self.data.len())
        }
    }
}

/// Custom chunk with registered handler
#[pyclass(name = "CustomChunk", module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyCustomChunk {
    #[pyo3(get)]
    pub uuid: String,
    #[pyo3(get)]
    pub data: Vec<u8>,
    #[pyo3(get)]
    pub handler_name: String,
}

impl PyCustomChunk {
    pub fn new(uuid: String, data: Vec<u8>, handler_name: String) -> Self {
        Self {
            uuid,
            data,
            handler_name,
        }
    }
}

impl TeehistorianChunk for PyCustomChunk {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        // Parse UUID string to uuid::Uuid
        let uuid_parsed = uuid::Uuid::parse_str(&self.uuid).unwrap_or_default();

        Chunk::UnknownEx(teehistorian::chunks::UnknownEx {
            uuid: uuid_parsed,
            data: &self.data,
        })
    }
}

#[pymethods]
impl PyCustomChunk {
    #[new]
    fn py_new(uuid: String, data: Vec<u8>, handler_name: String) -> Self {
        Self::new(uuid, data, handler_name)
    }

    fn __repr__(&self) -> String {
        self.py_repr()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        self.py_chunk_type()
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("uuid", &self.uuid)?;
        dict.set_item("data", &self.data)?;
        dict.set_item("handler_name", &self.handler_name)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }

    fn data_preview(&self) -> String {
        let preview_len = self.data.len().min(32);
        let hex: String = self.data[..preview_len]
            .iter()
            .map(|b| format!("{:02x}", b))
            .collect::<Vec<_>>()
            .join(" ");
        if self.data.len() > 32 {
            format!("{}... ({} bytes total)", hex, self.data.len())
        } else {
            format!("{} ({} bytes)", hex, self.data.len())
        }
    }
}

/// Generic/fallback chunk type
#[pyclass(name = "Generic", module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyGeneric {
    #[pyo3(get)]
    pub data: String,
}

impl PyGeneric {
    pub fn new(data: String) -> Self {
        Self { data }
    }
}

impl TeehistorianChunk for PyGeneric {
    fn to_teehistorian_chunk(&self) -> Chunk<'_> {
        // Generic chunks use NetMessage as fallback
        Chunk::NetMessage(teehistorian::chunks::NetMessage {
            cid: -1,
            msg: self.data.as_bytes(),
        })
    }
}

#[pymethods]
impl PyGeneric {
    #[new]
    fn py_new(data: String) -> Self {
        Self::new(data)
    }

    fn __repr__(&self) -> String {
        self.py_repr()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        self.py_chunk_type()
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", self.chunk_type())?;
        dict.set_item("data", &self.data)?;
        Ok(dict.into())
    }

    fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.py_write_to_buffer(py)
    }
}
