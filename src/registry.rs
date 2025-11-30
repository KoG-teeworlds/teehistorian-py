///! Chunk registration system for custom chunk types
///!
///! This module provides the infrastructure for registering and managing custom
///! chunk types that don't have direct teehistorian::Chunk enum variants.

use std::collections::HashMap;
use std::sync::Arc;
use parking_lot::RwLock;
use pyo3::prelude::*;

/// Field format types for custom chunks
#[pyclass(module = "teehistorian_py")]
#[derive(Debug, Clone, PartialEq)]
pub enum FieldFormat {
    /// Variable-width integer (teehistorian format)
    Varint,
    /// Fixed-width 8-bit integer
    I8,
    /// Fixed-width 16-bit integer
    I16,
    /// Fixed-width 32-bit integer
    I32,
    /// Fixed-width 64-bit integer
    I64,
    /// Length-prefixed UTF-8 string
    String,
    /// Length-prefixed raw bytes
    Bytes,
    /// 16-byte UUID
    Uuid,
}

#[pymethods]
impl FieldFormat {
    fn __repr__(&self) -> String {
        format!("{:?}", self)
    }
}

/// Field specification for a custom chunk
#[pyclass(module = "teehistorian_py")]
#[derive(Debug, Clone)]
pub struct FieldSpec {
    /// Field name
    #[pyo3(get, set)]
    pub name: String,
    /// Field format/encoding
    #[pyo3(get, set)]
    pub format: FieldFormat,
    /// Optional description
    #[pyo3(get, set)]
    pub description: Option<String>,
}

#[pymethods]
impl FieldSpec {
    #[new]
    fn new(name: String, format: FieldFormat, description: Option<String>) -> Self {
        Self { name, format, description }
    }

    fn __repr__(&self) -> String {
        format!("FieldSpec(name='{}', format={:?})", self.name, self.format)
    }
}

/// Custom chunk definition
#[pyclass(module = "teehistorian_py")]
#[derive(Debug, Clone)]
pub struct ChunkDef {
    /// UUID string for this chunk type
    #[pyo3(get, set)]
    pub uuid: String,
    /// Chunk type name (e.g., "MyCustomChunk")
    #[pyo3(get, set)]
    pub name: String,
    /// Field specifications in order
    #[pyo3(get, set)]
    pub fields: Vec<FieldSpec>,
}

#[pymethods]
impl ChunkDef {
    #[new]
    fn new(uuid: String, name: String, fields: Vec<FieldSpec>) -> Self {
        Self { uuid, name, fields }
    }

    fn __repr__(&self) -> String {
        format!("ChunkDef(uuid='{}', name='{}', {} fields)",
                self.uuid, self.name, self.fields.len())
    }
}

/// Global chunk registry
static GLOBAL_REGISTRY: once_cell::sync::Lazy<Arc<RwLock<HashMap<String, ChunkDef>>>> =
    once_cell::sync::Lazy::new(|| Arc::new(RwLock::new(HashMap::new())));

/// Register a chunk globally
pub fn register_global(chunk_def: ChunkDef) {
    let mut registry = GLOBAL_REGISTRY.write();
    registry.insert(chunk_def.uuid.clone(), chunk_def);
}

/// Unregister a chunk globally
pub fn unregister_global(uuid: &str) -> Option<ChunkDef> {
    let mut registry = GLOBAL_REGISTRY.write();
    registry.remove(uuid)
}

/// Get a chunk definition from the global registry
pub fn get_global(uuid: &str) -> Option<ChunkDef> {
    let registry = GLOBAL_REGISTRY.read();
    registry.get(uuid).cloned()
}

/// List all globally registered chunk UUIDs
pub fn list_global() -> Vec<String> {
    let registry = GLOBAL_REGISTRY.read();
    registry.keys().cloned().collect()
}

/// Instance-level chunk registry
///
/// This allows per-parser or per-writer chunk registrations that override global ones
#[derive(Debug, Clone, Default)]
pub struct InstanceRegistry {
    chunks: HashMap<String, ChunkDef>,
}

impl InstanceRegistry {
    /// Create a new empty instance registry
    pub fn new() -> Self {
        Self {
            chunks: HashMap::new(),
        }
    }

    /// Register a chunk in this instance
    pub fn register(&mut self, chunk_def: ChunkDef) {
        self.chunks.insert(chunk_def.uuid.clone(), chunk_def);
    }

    /// Unregister a chunk from this instance
    pub fn unregister(&mut self, uuid: &str) -> Option<ChunkDef> {
        self.chunks.remove(uuid)
    }

    /// Get a chunk definition, checking instance first, then global
    pub fn get(&self, uuid: &str) -> Option<ChunkDef> {
        // Check instance first
        if let Some(chunk_def) = self.chunks.get(uuid) {
            return Some(chunk_def.clone());
        }

        // Fall back to global
        get_global(uuid)
    }

    /// List all chunk UUIDs (instance + global)
    pub fn list_all(&self) -> Vec<String> {
        let mut uuids: Vec<String> = self.chunks.keys().cloned().collect();
        let global_uuids = list_global();

        for uuid in global_uuids {
            if !uuids.contains(&uuid) {
                uuids.push(uuid);
            }
        }

        uuids.sort();
        uuids
    }

    /// List only instance-level chunk UUIDs
    pub fn list_instance(&self) -> Vec<String> {
        let mut uuids: Vec<String> = self.chunks.keys().cloned().collect();
        uuids.sort();
        uuids
    }
}

/// Python module functions for chunk registration
pub mod py_api {
    use super::*;

    /// Register a chunk definition globally
    #[pyfunction]
    pub fn register_global_chunk(chunk_def: ChunkDef) {
        super::register_global(chunk_def);
    }

    /// Unregister a chunk from the global registry
    #[pyfunction]
    pub fn unregister_global_chunk(uuid: String) -> Option<ChunkDef> {
        super::unregister_global(&uuid)
    }

    /// Get a chunk definition from the global registry
    #[pyfunction]
    pub fn get_global_chunk(uuid: String) -> Option<ChunkDef> {
        super::get_global(&uuid)
    }

    /// List all globally registered chunk UUIDs
    #[pyfunction]
    pub fn list_global_chunks() -> Vec<String> {
        super::list_global()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_field_spec_creation() {
        let field = FieldSpec {
            name: "test_field".to_string(),
            format: FieldFormat::Varint,
            description: Some("A test field".to_string()),
        };

        assert_eq!(field.name, "test_field");
        assert_eq!(field.format, FieldFormat::Varint);
        assert!(field.description.is_some());
    }

    #[test]
    fn test_chunk_def_creation() {
        let fields = vec![
            FieldSpec {
                name: "client_id".to_string(),
                format: FieldFormat::Varint,
                description: None,
            },
            FieldSpec {
                name: "data".to_string(),
                format: FieldFormat::Bytes,
                description: None,
            },
        ];

        let chunk_def = ChunkDef::new(
            "test-uuid".to_string(),
            "TestChunk".to_string(),
            fields.clone(),
        );

        assert_eq!(chunk_def.uuid, "test-uuid");
        assert_eq!(chunk_def.name, "TestChunk");
        assert_eq!(chunk_def.fields.len(), 2);
    }

    #[test]
    fn test_instance_registry() {
        let mut registry = InstanceRegistry::new();

        let chunk_def = ChunkDef::new(
            "instance-uuid".to_string(),
            "InstanceChunk".to_string(),
            vec![],
        );

        // Register
        registry.register(chunk_def.clone());

        // Get
        let retrieved = registry.get("instance-uuid");
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().name, "InstanceChunk");

        // List instance
        let instance_uuids = registry.list_instance();
        assert_eq!(instance_uuids.len(), 1);
        assert_eq!(instance_uuids[0], "instance-uuid");

        // Unregister
        let removed = registry.unregister("instance-uuid");
        assert!(removed.is_some());
        assert_eq!(removed.unwrap().name, "InstanceChunk");

        // Verify removed
        assert!(registry.get("instance-uuid").is_none());
    }
}
