//! Declarative macros for reducing chunk definition boilerplate
//!
//! This module provides powerful macros that eliminate repetitive code
//! when defining teehistorian chunk types.

// Re-export paste for use in macros
#[doc(hidden)]
pub use paste::paste;

/// Define a simple chunk type with automatic trait implementations
///
/// This macro generates:
/// - PyClass struct with frozen attribute
/// - Debug and Clone derives
/// - All fields marked with #[pyo3(get)]
/// - TeehistorianChunk trait implementation
/// - Complete pymethods block with all standard methods
///
/// # Syntax
/// ```ignore
/// define_chunk! {
///     /// Documentation for the chunk
///     ChunkName(teehistorian_variant_name) {
///         field_name: RustType => teehistorian_field_name,
///         another_field: RustType => another_teehistorian_field,
///     }
/// }
/// ```
///
/// # Example
/// ```ignore
/// define_chunk! {
///     /// Player joins the server
///     Join(Join) {
///         client_id: i32 => cid,
///     }
/// }
/// ```
#[macro_export]
macro_rules! define_chunk {
    (
        $(#[$meta:meta])*
        $name:ident($teehistorian_variant:ident) {
            $(
                $(#[$field_meta:meta])*
                $field:ident: $field_ty:ty => $teehistorian_field:ident
            ),* $(,)?
        }
    ) => {
        $crate::macros::paste! {
            $(#[$meta])*
            #[pyclass(module = "teehistorian_py", frozen)]
            #[derive(Debug, Clone)]
            pub struct [<Py $name>] {
            $(
                $(#[$field_meta])*
                #[pyo3(get)]
                pub $field: $field_ty,
            )*
        }

        impl [<Py $name>] {
            pub fn new($($field: $field_ty),*) -> Self {
                Self {
                    $($field),*
                }
            }
        }

        impl $crate::chunks::TeehistorianChunk for [<Py $name>] {
            fn to_teehistorian_chunk(&self) -> teehistorian::Chunk<'_> {
                teehistorian::Chunk::$teehistorian_variant(
                    teehistorian::chunks::$teehistorian_variant {
                        $(
                            $teehistorian_field: define_chunk!(@convert_field self.$field, $field_ty),
                        )*
                    }
                )
            }
        }

        #[pymethods]
        impl [<Py $name>] {
            #[new]
            fn py_new($($field: $field_ty),*) -> Self {
                Self::new($($field),*)
            }

            fn __repr__(&self) -> String {
                $crate::chunks::PyChunkMethods::py_repr(self)
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            fn chunk_type(&self) -> &'static str {
                $crate::chunks::PyChunkMethods::py_chunk_type(self)
            }

            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", self.chunk_type())?;
                $(
                    dict.set_item(stringify!($field), &self.$field)?;
                )*
                Ok(dict.into())
            }

            fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                self.py_write_to_buffer(py)
            }
        }
        }
    };

    // Helper: Convert field value based on type for teehistorian
    (@convert_field $value:expr, String) => {
        $value.as_bytes()
    };
    (@convert_field $value:expr, Vec<u8>) => {
        $value.as_slice()
    };
    (@convert_field $value:expr, $ty:ty) => {
        $value
    };
}

/// Define a chunk with custom field conversions
///
/// Use this when fields need special handling during serialization.
///
/// # Syntax
/// ```ignore
/// define_chunk_custom! {
///     ChunkName(VariantName::StructName) { fields... }
/// }
/// // or for same names:
/// define_chunk_custom! {
///     ChunkName(VariantName) { fields... }
/// }
/// ```
///
/// # Example
/// ```ignore
/// define_chunk_custom! {
///     /// DDNet version information
///     DdnetVersion(DdnetVersion) {
///         client_id: i32 => cid,
///         connection_id: String => connection_id [as_bytes],
///         version: i32 => version,
///         version_str: Vec<u8> => version_str [as_slice],
///     }
/// }
///
/// define_chunk_custom! {
///     /// Auth login with different names
///     AuthLogin(AuthLogin::Auth) {
///         client_id: i32 => cid,
///         level: i32 => level,
///         auth_name: String => auth_name [as_bytes],
///     }
/// }
/// ```
#[macro_export]
macro_rules! define_chunk_custom {
    // Version with separate variant and struct names
    (
        $(#[$meta:meta])*
        $name:ident($teehistorian_variant:ident :: $teehistorian_struct:ident) {
            $(
                $(#[$field_meta:meta])*
                $field:ident: $field_ty:ty => $teehistorian_field:ident $([$conversion:ident])?
            ),* $(,)?
        }
    ) => {
        $crate::macros::paste! {
            $(#[$meta])*
            #[pyclass(module = "teehistorian_py", frozen)]
            #[derive(Debug, Clone)]
            pub struct [<Py $name>] {
            $(
                $(#[$field_meta])*
                #[pyo3(get)]
                pub $field: $field_ty,
            )*
        }

        impl [<Py $name>] {
            pub fn new($($field: $field_ty),*) -> Self {
                Self {
                    $($field),*
                }
            }
        }

        impl $crate::chunks::TeehistorianChunk for [<Py $name>] {
            fn to_teehistorian_chunk(&self) -> teehistorian::Chunk<'_> {
                teehistorian::Chunk::$teehistorian_variant(
                    teehistorian::chunks::$teehistorian_struct {
                        $(
                            $teehistorian_field: define_chunk_custom!(@apply_conversion self.$field, $($conversion)?),
                        )*
                    }
                )
            }
        }

        #[pymethods]
        impl [<Py $name>] {
            #[new]
            fn py_new($($field: $field_ty),*) -> Self {
                Self::new($($field),*)
            }

            fn __repr__(&self) -> String {
                $crate::chunks::PyChunkMethods::py_repr(self)
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            fn chunk_type(&self) -> &'static str {
                $crate::chunks::PyChunkMethods::py_chunk_type(self)
            }

            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", self.chunk_type())?;
                $(
                    dict.set_item(stringify!($field), &self.$field)?;
                )*
                Ok(dict.into())
            }

            fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                self.py_write_to_buffer(py)
            }
        }
        }
    };

    // Version with same name for both variant and struct
    (
        $(#[$meta:meta])*
        $name:ident($teehistorian_variant:ident) {
            $(
                $(#[$field_meta:meta])*
                $field:ident: $field_ty:ty => $teehistorian_field:ident $([$conversion:ident])?
            ),* $(,)?
        }
    ) => {
        $crate::macros::paste! {
            $(#[$meta])*
            #[pyclass(module = "teehistorian_py", frozen)]
            #[derive(Debug, Clone)]
            pub struct [<Py $name>] {
            $(
                $(#[$field_meta])*
                #[pyo3(get)]
                pub $field: $field_ty,
            )*
        }

        impl [<Py $name>] {
            pub fn new($($field: $field_ty),*) -> Self {
                Self {
                    $($field),*
                }
            }
        }

        impl $crate::chunks::TeehistorianChunk for [<Py $name>] {
            fn to_teehistorian_chunk(&self) -> teehistorian::Chunk<'_> {
                teehistorian::Chunk::$teehistorian_variant(
                    teehistorian::chunks::$teehistorian_variant {
                        $(
                            $teehistorian_field: define_chunk_custom!(@apply_conversion self.$field, $($conversion)?),
                        )*
                    }
                )
            }
        }

        #[pymethods]
        impl [<Py $name>] {
            #[new]
            fn py_new($($field: $field_ty),*) -> Self {
                Self::new($($field),*)
            }

            fn __repr__(&self) -> String {
                $crate::chunks::PyChunkMethods::py_repr(self)
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            fn chunk_type(&self) -> &'static str {
                $crate::chunks::PyChunkMethods::py_chunk_type(self)
            }

            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", self.chunk_type())?;
                $(
                    dict.set_item(stringify!($field), &self.$field)?;
                )*
                Ok(dict.into())
            }

            fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                $crate::chunks::PyChunkMethods::py_write_to_buffer(self, py)
            }
        }
        }  // End paste!
    };

    // Helper: Apply conversion methods
    (@apply_conversion $value:expr, as_str) => {
        $value.as_str()
    };
    (@apply_conversion $value:expr, as_bytes) => {
        $value.as_bytes()
    };
    (@apply_conversion $value:expr, as_slice) => {
        $value.as_slice()
    };
    (@apply_conversion $value:expr, as_uuid) => {
        uuid::Uuid::parse_str(&$value).unwrap_or_default()
    };
    (@apply_conversion $value:expr, as_args_vec) => {{
        // Convert string to Vec<&[u8]> for console command args
        // Split by null bytes and collect
        let bytes = $value.as_bytes();
        vec![bytes]
    }};
    (@apply_conversion $value:expr, ) => {
        $value
    };
}

/// Define an inline struct chunk (like Join { cid: i32 })
///
/// For chunks where the teehistorian enum variant is an inline struct,
/// not a tuple variant containing a struct.
///
/// # Example
/// ```ignore
/// define_inline_chunk! {
///     /// Player joins the server
///     Join {
///         client_id: i32 => cid,
///     }
/// }
/// ```
#[macro_export]
macro_rules! define_inline_chunk {
    (
        $(#[$meta:meta])*
        $name:ident {
            $(
                $(#[$field_meta:meta])*
                $field:ident: $field_ty:ty => $teehistorian_field:ident
            ),* $(,)?
        }
    ) => {
        $crate::macros::paste! {
            $(#[$meta])*
            #[pyclass(module = "teehistorian_py", frozen)]
            #[derive(Debug, Clone)]
            pub struct [<Py $name>] {
            $(
                $(#[$field_meta])*
                #[pyo3(get)]
                pub $field: $field_ty,
            )*
        }

        impl [<Py $name>] {
            pub fn new($($field: $field_ty),*) -> Self {
                Self {
                    $($field),*
                }
            }
        }

        impl $crate::chunks::TeehistorianChunk for [<Py $name>] {
            fn to_teehistorian_chunk(&self) -> teehistorian::Chunk<'_> {
                teehistorian::Chunk::$name {
                    $(
                        $teehistorian_field: define_inline_chunk!(@convert_field self.$field, $field_ty),
                    )*
                }
            }
        }

        #[pymethods]
        impl [<Py $name>] {
            #[new]
            fn py_new($($field: $field_ty),*) -> Self {
                Self::new($($field),*)
            }

            fn __repr__(&self) -> String {
                $crate::chunks::PyChunkMethods::py_repr(self)
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            fn chunk_type(&self) -> &'static str {
                $crate::chunks::PyChunkMethods::py_chunk_type(self)
            }

            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", self.chunk_type())?;
                $(
                    dict.set_item(stringify!($field), &self.$field)?;
                )*
                Ok(dict.into())
            }

            fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                $crate::chunks::PyChunkMethods::py_write_to_buffer(self, py)
            }
        }
        }  // End paste!
    };

    // Helper: Convert field value based on type for teehistorian
    (@convert_field $value:expr, String) => {
        $value.as_bytes()
    };
    (@convert_field $value:expr, Vec<u8>) => {
        $value.as_slice()
    };
    (@convert_field $value:expr, $ty:ty) => {
        $value
    };
}

/// Define a zero-field chunk (like Eos)
///
/// # Example
/// ```ignore
/// define_zero_field_chunk! {
///     /// End of stream marker
///     Eos(Eos)
/// }
/// ```
#[macro_export]
macro_rules! define_zero_field_chunk {
    (
        $(#[$meta:meta])*
        $name:ident($teehistorian_variant:ident)
    ) => {
        $crate::macros::paste! {
            $(#[$meta])*
            #[pyclass(module = "teehistorian_py", frozen)]
            #[derive(Debug, Clone)]
            pub struct [<Py $name>];

        impl [<Py $name>] {
            pub fn new() -> Self {
                Self
            }
        }

        impl Default for [<Py $name>] {
            fn default() -> Self {
                Self::new()
            }
        }

        impl $crate::chunks::TeehistorianChunk for [<Py $name>] {
            fn to_teehistorian_chunk(&self) -> teehistorian::Chunk<'_> {
                teehistorian::Chunk::$teehistorian_variant
            }
        }

        #[pymethods]
        impl [<Py $name>] {
            #[new]
            fn py_new() -> Self {
                Self::new()
            }

            fn __repr__(&self) -> String {
                format!("{}()", stringify!($name))
            }

            fn __str__(&self) -> String {
                self.__repr__()
            }

            fn chunk_type(&self) -> &'static str {
                stringify!($name)
            }

            fn to_dict(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                let dict = pyo3::types::PyDict::new(py);
                dict.set_item("type", self.chunk_type())?;
                Ok(dict.into())
            }

            fn write_to_buffer(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
                $crate::chunks::PyChunkMethods::py_write_to_buffer(self, py)
            }
        }
        }  // End paste!
    };
}

/// Batch define multiple simple chunks with the same pattern
///
/// This is useful for defining many chunks that follow the exact same pattern.
///
/// # Example
/// ```ignore
/// batch_define_chunks! {
///     // All take just client_id
///     simple_client_id: [
///         Join => Join,
///         JoinVer6 => JoinVer6,
///         PlayerReady => PlayerReady,
///         PlayerOld => PlayerOld,
///     ]
/// }
/// ```
#[macro_export]
macro_rules! batch_define_chunks {
    (
        simple_client_id: [
            $(
                $(#[$meta:meta])*
                $name:ident => $variant:ident
            ),* $(,)?
        ]
    ) => {
        $(
            define_chunk! {
                $(#[$meta])*
                $name($variant) {
                    client_id: i32 => cid,
                }
            }
        )*
    };
}
