use pyo3::prelude::*;

/// Macro to generate chunk classes without inheritance
macro_rules! define_chunk {
    (
        $(#[$meta:meta])*
        $name:ident => $pyname:literal {
            $($field:ident: $type:ty),* $(,)?
        }
    ) => {
        $(#[$meta])*
        #[pyclass(name = $pyname, module = "teehistorian_py", frozen)]
        #[derive(Debug, Clone)]
        pub struct $name {
            $(
                #[pyo3(get)]
                pub $field: $type,
            )*
        }

        impl $name {
            /// Rust constructor
            pub fn new($($field: $type),*) -> Self {
                Self { $($field),* }
            }
        }

        #[pymethods]
        impl $name {
            #[new]
            fn py_new($($field: $type),*) -> Self {
                Self::new($($field),*)
            }

            fn __repr__(&self) -> String {
                let mut repr = format!("{}(", stringify!($name).strip_prefix("Py").unwrap_or(stringify!($name)));
                let mut _first = true;
                $(
                    if !_first {
                        repr.push_str(", ");
                    }
                    repr.push_str(&format!("{}={:?}", stringify!($field), self.$field));
                    _first = false;
                )*
                repr.push(')');
                repr
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            /// Get the chunk type as a string
            fn chunk_type(&self) -> &'static str {
                $pyname
            }

            /// Convert to dictionary for easier inspection
            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", $pyname)?;
                $(
                    dict.set_item(stringify!($field), &self.$field)?;
                )*
                Ok(dict.into())
            }
        }
    };
}

// Player Lifecycle Chunks

define_chunk! {
    /// Player joins the server
    PyJoin => "Join" {
        client_id: i32,
    }
}

define_chunk! {
    /// Player joins with version 6 protocol
    PyJoinVer6 => "JoinVer6" {
        client_id: i32,
    }
}

define_chunk! {
    /// Player disconnects from the server
    PyDrop => "Drop" {
        client_id: i32,
        reason: String,
    }
}

define_chunk! {
    /// Player becomes ready to play
    PyPlayerReady => "PlayerReady" {
        client_id: i32,
    }
}

// Player State Chunks

define_chunk! {
    /// New player spawn position
    PyPlayerNew => "PlayerNew" {
        client_id: i32,
        x: i32,
        y: i32,
    }
}

define_chunk! {
    /// Player leaves the game (but not server)
    PyPlayerOld => "PlayerOld" {
        client_id: i32,
    }
}

define_chunk! {
    /// Player changes team
    PyPlayerTeam => "PlayerTeam" {
        client_id: i32,
        team: i32,
    }
}

define_chunk! {
    /// Player changes name
    PyPlayerName => "PlayerName" {
        client_id: i32,
        name: String,
    }
}

define_chunk! {
    /// Player position difference/update
    PyPlayerDiff => "PlayerDiff" {
        client_id: i32,
        dx: i32,
        dy: i32,
    }
}

// Input Chunks

define_chunk! {
    /// New player input state
    PyInputNew => "InputNew" {
        client_id: i32,
        input: String,
    }
}

define_chunk! {
    /// Player input difference from previous state
    PyInputDiff => "InputDiff" {
        client_id: i32,
        input: Vec<i32>,
    }
}

// Communication Chunks

define_chunk! {
    /// Network message from/to player
    PyNetMessage => "NetMessage" {
        client_id: i32,
        message: String,
    }
}

define_chunk! {
    /// Console command executed by player
    PyConsoleCommand => "ConsoleCommand" {
        client_id: i32,
        flags: i32,
        command: String,
        args: String,
    }
}

// Authentication & Version Chunks

define_chunk! {
    /// Player authentication/login
    PyAuthLogin => "AuthLogin" {
        client_id: i32,
        level: i32,
        name: String,
    }
}

define_chunk! {
    /// DDNet client version information
    PyDdnetVersion => "DdnetVersion" {
        client_id: i32,
        connection_id: String,
        version: i32,
        version_str: Vec<u8>,
    }
}

// Server Event Chunks

define_chunk! {
    /// Server tick skip
    PyTickSkip => "TickSkip" {
        dt: i32,
    }
}

define_chunk! {
    /// Team save loaded successfully
    PyTeamLoadSuccess => "TeamLoadSuccess" {
        team: i32,
        save: String,
    }
}

define_chunk! {
    /// Team save load failed
    PyTeamLoadFailure => "TeamLoadFailure" {
        team: i32,
    }
}

define_chunk! {
    /// Anti-bot system event
    PyAntiBot => "AntiBot" {
        data: String,
    }
}

// Special Chunks

/// End of stream marker
#[pyclass(name = "Eos", module = "teehistorian_py", frozen)]
#[derive(Debug, Clone)]
pub struct PyEos;

impl Default for PyEos {
    fn default() -> Self {
        Self::new()
    }
}

impl PyEos {
    /// Rust constructor
    pub fn new() -> Self {
        Self
    }
}

#[pymethods]
impl PyEos {
    #[new]
    fn py_new() -> Self {
        Self::new()
    }

    fn __repr__(&self) -> String {
        "Eos()".to_string()
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn chunk_type(&self) -> &'static str {
        "Eos"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", "Eos")?;
        Ok(dict.into())
    }
}

/// Unknown chunk with UUID
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

#[pymethods]
impl PyUnknown {
    #[new]
    fn py_new(uuid: String, data: Vec<u8>) -> Self {
        Self::new(uuid, data)
    }

    fn __repr__(&self) -> String {
        format!(
            "Unknown(uuid='{}', data_len={})",
            self.uuid,
            self.data.len()
        )
    }

    fn __str__(&self) -> String {
        format!("Unknown chunk with UUID: {}", self.uuid)
    }

    fn chunk_type(&self) -> &'static str {
        "Unknown"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", "Unknown")?;
        dict.set_item("uuid", &self.uuid)?;
        dict.set_item("data_length", self.data.len())?;
        Ok(dict.into())
    }

    /// Get a hex preview of the data (first 32 bytes)
    fn data_preview(&self) -> String {
        let preview_len = std::cmp::min(32, self.data.len());
        let preview = &self.data[..preview_len];
        let hex = preview
            .iter()
            .map(|b| format!("{:02x}", b))
            .collect::<String>();

        if self.data.len() > 32 {
            format!("{}... ({} bytes total)", hex, self.data.len())
        } else {
            hex
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

#[pymethods]
impl PyCustomChunk {
    #[new]
    fn py_new(uuid: String, data: Vec<u8>, handler_name: String) -> Self {
        Self::new(uuid, data, handler_name)
    }

    fn __repr__(&self) -> String {
        format!(
            "CustomChunk(uuid='{}', handler='{}', data_len={})",
            self.uuid,
            self.handler_name,
            self.data.len()
        )
    }

    fn __str__(&self) -> String {
        format!("Custom chunk handled by: {}", self.handler_name)
    }

    fn chunk_type(&self) -> &'static str {
        "CustomChunk"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", "CustomChunk")?;
        dict.set_item("uuid", &self.uuid)?;
        dict.set_item("handler_name", &self.handler_name)?;
        dict.set_item("data_length", self.data.len())?;
        Ok(dict.into())
    }

    /// Get a hex preview of the data (first 32 bytes)
    fn data_preview(&self) -> String {
        let preview_len = std::cmp::min(32, self.data.len());
        let preview = &self.data[..preview_len];
        let hex = preview
            .iter()
            .map(|b| format!("{:02x}", b))
            .collect::<String>();

        if self.data.len() > 32 {
            format!("{}... ({} bytes total)", hex, self.data.len())
        } else {
            hex
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

#[pymethods]
impl PyGeneric {
    #[new]
    fn py_new(data: String) -> Self {
        Self::new(data)
    }

    fn __repr__(&self) -> String {
        let preview = if self.data.len() > 50 {
            format!("{}...", &self.data[..50])
        } else {
            self.data.clone()
        };
        format!("Generic(data='{}')", preview)
    }

    fn __str__(&self) -> String {
        format!("Generic chunk: {}", self.data)
    }

    fn chunk_type(&self) -> &'static str {
        "Generic"
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("type", "Generic")?;
        dict.set_item("data", &self.data)?;
        Ok(dict.into())
    }
}
