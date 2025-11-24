use quote::quote;
use std::{collections::BTreeMap, env, fs, path::PathBuf};
use syn::{Attribute, Fields, Item, ItemStruct, Meta, Type, Visibility, parse_file};

fn main() {
    println!("cargo:rerun-if-changed=src/chunks.rs");
    println!("cargo:rerun-if-changed=src/lib.rs");
    println!("cargo:rerun-if-changed=src/errors.rs");
    println!("cargo:rerun-if-changed=src/handlers.rs");
    println!("cargo:rerun-if-changed=src/writer.rs");
    println!("cargo:rerun-if-changed=src/python/teehistorian_py");

    // Extract chunks from source
    let chunks = extract_chunks_from_source();

    // Generate type stubs from source
    let pyi_content = generate_pyi(&chunks);

    // Write the .pyi file to both the output directory and the package directory
    let out_dir = env::var("OUT_DIR").unwrap();
    let pyi_out_path = PathBuf::from(&out_dir).join("_rust.pyi");
    fs::write(&pyi_out_path, &pyi_content).expect("Failed to write .pyi file to OUT_DIR");

    // Also write to the Python package directory for development
    let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
    let package_pyi_path =
        PathBuf::from(&manifest_dir).join("src/python/teehistorian_py/_rust.pyi");

    // Create parent directories if they don't exist
    if let Some(parent) = package_pyi_path.parent() {
        fs::create_dir_all(parent).ok();
    }

    fs::write(&package_pyi_path, &pyi_content)
        .expect("Failed to write .pyi file to package directory");

    println!(
        "cargo:warning=Generated type stubs at {} and {}",
        pyi_out_path.display(),
        package_pyi_path.display()
    );
}

/// Represents a chunk type extracted from Rust source
#[derive(Debug, Clone, Eq, PartialEq, Ord, PartialOrd)]
struct ChunkInfo {
    /// Python class name (without "Py" prefix)
    name: String,
    /// Class documentation
    doc: Option<String>,
    /// Fields with their types
    fields: Vec<(String, String)>,
    /// Category of the chunk
    category: String,
}

/// Extract all chunks from chunks.rs
fn extract_chunks_from_source() -> Vec<ChunkInfo> {
    let mut chunks = Vec::new();

    let chunks_path = PathBuf::from("src/chunks.rs");
    if let Ok(content) = fs::read_to_string(&chunks_path)
        && let Ok(file) = parse_file(&content)
    {
        for item in file.items {
            if let Item::Struct(item_struct) = item {
                // Only process PyXXX structs that are public
                if item_struct
                    .attrs
                    .iter()
                    .any(|attr| attr.path().is_ident("pyclass"))
                    && matches!(item_struct.vis, Visibility::Public(_))
                    && let Some(chunk_info) = extract_chunk_info(&item_struct)
                {
                    chunks.push(chunk_info);
                }
            }
        }
    }

    // Sort for consistent output
    chunks.sort();
    chunks
}

/// Extract chunk_category from doc comments or attributes
/// Looks for patterns like "Category: PlayerLifecycle" in doc comments
fn extract_chunk_category(attrs: &[Attribute]) -> Option<String> {
    // First try to find it in doc comments (format: "Category: CategoryName")
    for attr in attrs {
        if attr.path().is_ident("doc")
            && let Meta::NameValue(nv) = &attr.meta
            && let syn::Expr::Lit(expr_lit) = &nv.value
            && let syn::Lit::Str(lit_str) = &expr_lit.lit
        {
            let doc = lit_str.value();
            if let Some(pos) = doc.find("Category:") {
                let category_part = &doc[pos + 9..];
                let category = category_part.split_whitespace().next().unwrap_or("");
                if !category.is_empty() {
                    return Some(category.to_string());
                }
            }
        }
    }

    // Fallback: try the old chunk_category attribute (for backwards compatibility)
    for attr in attrs {
        if attr.path().is_ident("chunk_category")
            && let Meta::NameValue(nv) = &attr.meta
            && let syn::Expr::Lit(expr_lit) = &nv.value
            && let syn::Lit::Str(lit_str) = &expr_lit.lit
        {
            return Some(lit_str.value().trim().to_string());
        }
    }
    None
}

/// Extract information about a chunk struct
fn extract_chunk_info(item_struct: &ItemStruct) -> Option<ChunkInfo> {
    let struct_name = item_struct.ident.to_string();

    // Skip base PyChunk class
    if struct_name == "PyChunk" {
        return None;
    }

    // Get Python class name (remove Py prefix)
    let name = struct_name
        .strip_prefix("Py")
        .unwrap_or(&struct_name)
        .to_string();

    // Extract doc comments
    let doc = extract_doc_comments(&item_struct.attrs);

    // Extract category from attribute, or default to "Other"
    let category =
        extract_chunk_category(&item_struct.attrs).unwrap_or_else(|| "Other".to_string());

    // Extract fields
    let mut fields = Vec::new();
    if let Fields::Named(named_fields) = &item_struct.fields {
        for field in &named_fields.named {
            if let Some(field_name) = &field.ident
                && field.attrs.iter().any(|attr| {
                    attr.path().is_ident("pyo3")
                        && attr
                            .parse_args::<syn::Ident>()
                            .map(|id| id == "get")
                            .unwrap_or(false)
                })
            {
                let py_type = rust_type_to_python(&field.ty);
                fields.push((field_name.to_string(), py_type));
            }
        }
    }

    Some(ChunkInfo {
        name,
        doc,
        fields,
        category,
    })
}

/// Extract doc comments from attributes
fn extract_doc_comments(attrs: &[Attribute]) -> Option<String> {
    let docs: Vec<String> = attrs
        .iter()
        .filter_map(|attr| {
            if attr.path().is_ident("doc")
                && let Meta::NameValue(nv) = &attr.meta
                && let syn::Expr::Lit(expr_lit) = &nv.value
                && let syn::Lit::Str(lit_str) = &expr_lit.lit
            {
                return Some(lit_str.value().trim().to_string());
            }
            None
        })
        .collect();

    if docs.is_empty() {
        None
    } else {
        Some(docs.join("\n"))
    }
}

/// Generate the .pyi file content
fn generate_pyi(chunks: &[ChunkInfo]) -> String {
    let mut pyi = String::new();

    // Header
    pyi.push_str("# Type stubs for teehistorian_py._rust\n");
    pyi.push_str("# Auto-generated from Rust source code by build.rs\n");
    pyi.push_str("# Do not edit manually\n\n");

    // Imports
    pyi.push_str("from typing import (\n");
    pyi.push_str("    Any,\n");
    pyi.push_str("    Dict,\n");
    pyi.push_str("    Iterator,\n");
    pyi.push_str("    List,\n");
    pyi.push_str("    Optional,\n");
    pyi.push_str("    Protocol,\n");
    pyi.push_str("    Union,\n");
    pyi.push_str(")\n\n");

    // Version and doc
    pyi.push_str("__version__: str\n");
    pyi.push_str("__doc__: str\n\n");

    // Exceptions
    pyi.push_str(
        "# ============================================================================\n",
    );
    pyi.push_str("# Exceptions\n");
    pyi.push_str(
        "# ============================================================================\n\n",
    );
    pyi.push_str("class TeehistorianError(Exception):\n");
    pyi.push_str("    \"\"\"Base exception for all teehistorian parsing and writing errors.\n\n");
    pyi.push_str("    This exception is raised for any errors that occur during parsing,\n");
    pyi.push_str("    writing, or validation of teehistorian files.\n");
    pyi.push_str("    \"\"\"\n\n");
    pyi.push_str("    def __init__(self, message: str) -> None: ...\n\n");

    // Parser class
    pyi.push_str(
        "# ============================================================================\n",
    );
    pyi.push_str("# Parser\n");
    pyi.push_str(
        "# ============================================================================\n\n",
    );
    pyi.push_str("class Teehistorian:\n");
    pyi.push_str("    \"\"\"High-performance teehistorian file parser.\n\n");
    pyi.push_str("    This class provides efficient parsing of teehistorian files using the\n");
    pyi.push_str("    Rust backend. It supports iteration over chunks and custom UUID handler\n");
    pyi.push_str("    registration for extensibility.\n");
    pyi.push_str("    \"\"\"\n\n");
    pyi.push_str("    def __init__(self, data: bytes) -> None:\n");
    pyi.push_str("        \"\"\"Initialize parser with raw teehistorian data.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            data: Raw bytes from a teehistorian file\n\n");
    pyi.push_str("        Raises:\n");
    pyi.push_str("            TeehistorianError: If data is empty or invalid\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def register_custom_uuid(self, uuid_string: str) -> None:\n");
    pyi.push_str("        \"\"\"Register a custom UUID handler for chunk parsing.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str(
        "            uuid_string: UUID in format XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX\n\n",
    );
    pyi.push_str("        Raises:\n");
    pyi.push_str("            TeehistorianError: If UUID format is invalid\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def header(self) -> bytes:\n");
    pyi.push_str("        \"\"\"Get the teehistorian header as raw bytes.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Header data as bytes (typically JSON)\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    @property\n");
    pyi.push_str("    def chunk_count(self) -> int:\n");
    pyi.push_str("        \"\"\"Number of chunks processed so far.\"\"\"\n\n");
    pyi.push_str("    def get_registered_uuids(self) -> List[str]:\n");
    pyi.push_str("        \"\"\"Get all registered custom UUID handlers.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            List of registered UUID strings\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def __iter__(self) -> Iterator[Any]:\n");
    pyi.push_str("        \"\"\"Iterate over chunks in the teehistorian.\"\"\"\n\n");
    pyi.push_str("    def __next__(self) -> Any:\n");
    pyi.push_str("        \"\"\"Get next chunk from the stream.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Next chunk object\n\n");
    pyi.push_str("        Raises:\n");
    pyi.push_str("            StopIteration: When end of stream is reached\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def __enter__(self) -> 'Teehistorian':\n");
    pyi.push_str("        \"\"\"Context manager entry.\"\"\"\n\n");
    pyi.push_str("    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:\n");
    pyi.push_str("        \"\"\"Context manager exit.\"\"\"\n\n");

    // Writer class
    pyi.push_str(
        "# ============================================================================\n",
    );
    pyi.push_str("# Writer\n");
    pyi.push_str(
        "# ============================================================================\n\n",
    );
    pyi.push_str("class TeehistorianWriter:\n");
    pyi.push_str("    \"\"\"Writer for creating teehistorian files programmatically.\n\n");
    pyi.push_str("    This class provides functionality to create valid teehistorian files\n");
    pyi.push_str("    by writing chunks and configuring headers. Supports method chaining\n");
    pyi.push_str("    and context manager protocol for clean resource management.\n");
    pyi.push_str("    \"\"\"\n\n");
    pyi.push_str("    def __init__(self, file: Optional[Any] = None) -> None:\n");
    pyi.push_str("        \"\"\"Initialize a new teehistorian writer.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            file: Optional file-like object (for future use)\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def write(self, chunk: Any) -> 'TeehistorianWriter':\n");
    pyi.push_str("        \"\"\"Write a chunk to the teehistorian.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            chunk: A chunk object to write\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Self for method chaining\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def write_all(self, chunks: List[Any]) -> 'TeehistorianWriter':\n");
    pyi.push_str("        \"\"\"Write multiple chunks at once.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            chunks: List of chunk objects to write\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Self for method chaining\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def set_header(self, key: str, value: str) -> 'TeehistorianWriter':\n");
    pyi.push_str("        \"\"\"Set a header field value.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            key: Header field name\n");
    pyi.push_str("            value: Header field value\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Self for method chaining\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def get_header(self, key: str) -> Optional[str]:\n");
    pyi.push_str("        \"\"\"Get a header field value.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            key: Header field name\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Header value or None if not set\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str(
        "    def update_headers(self, headers: Dict[str, str]) -> 'TeehistorianWriter':\n",
    );
    pyi.push_str("        \"\"\"Update multiple header fields from a dictionary.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            headers: Dictionary of field names to values\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Self for method chaining\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def getvalue(self) -> bytes:\n");
    pyi.push_str("        \"\"\"Get all written data as bytes.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Complete teehistorian file as bytes\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def save(self, path: str) -> None:\n");
    pyi.push_str("        \"\"\"Save the teehistorian to a file.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            path: File path to save to\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def writeto(self, file: Any) -> None:\n");
    pyi.push_str("        \"\"\"Write all data to a file-like object.\n\n");
    pyi.push_str("        Args:\n");
    pyi.push_str("            file: File-like object with write() method\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def size(self) -> int:\n");
    pyi.push_str("        \"\"\"Get current buffer size in bytes.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Number of bytes written\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def reset(self) -> None:\n");
    pyi.push_str("        \"\"\"Reset the writer to initial empty state.\n\n");
    pyi.push_str("        Clears all written data and resets headers to defaults.\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def is_empty(self) -> bool:\n");
    pyi.push_str("        \"\"\"Check if any data has been written.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            True if nothing has been written yet\n");
    pyi.push_str("        \"\"\"\n\n");
    pyi.push_str("    def __enter__(self) -> 'TeehistorianWriter':\n");
    pyi.push_str("        \"\"\"Context manager entry.\"\"\"\n\n");
    pyi.push_str("    def __exit__(\n");
    pyi.push_str("        self,\n");
    pyi.push_str("        exc_type: Optional[type],\n");
    pyi.push_str("        exc_val: Optional[Exception],\n");
    pyi.push_str("        exc_tb: Optional[Any],\n");
    pyi.push_str("    ) -> bool:\n");
    pyi.push_str("        \"\"\"Context manager exit.\"\"\"\n\n");
    pyi.push_str("    def __repr__(self) -> str:\n");
    pyi.push_str("        \"\"\"Get string representation.\"\"\"\n\n");

    // Base Chunk class
    pyi.push_str(
        "# ============================================================================\n",
    );
    pyi.push_str("# Chunk Types\n");
    pyi.push_str(
        "# ============================================================================\n\n",
    );
    pyi.push_str("class Chunk:\n");
    pyi.push_str("    \"\"\"Base class for all teehistorian chunk types.\n\n");
    pyi.push_str("    All chunk types inherit from this base class, providing a common\n");
    pyi.push_str("    interface for chunk operations and serialization.\n");
    pyi.push_str("    \"\"\"\n\n");
    pyi.push_str("    def chunk_type(self) -> str:\n");
    pyi.push_str("        \"\"\"Get the chunk type identifier.\"\"\"\n\n");
    pyi.push_str("    def __repr__(self) -> str:\n");
    pyi.push_str("        \"\"\"Get string representation for debugging.\"\"\"\n\n");
    pyi.push_str("    def __str__(self) -> str:\n");
    pyi.push_str("        \"\"\"Get human-readable string representation.\"\"\"\n\n");
    pyi.push_str("    def to_dict(self) -> Dict[str, Any]:\n");
    pyi.push_str("        \"\"\"Convert chunk to dictionary representation.\n\n");
    pyi.push_str("        Returns:\n");
    pyi.push_str("            Dictionary with chunk data including 'type' field\n");
    pyi.push_str("        \"\"\"\n\n");

    // Group chunks by category
    let mut chunks_by_category: BTreeMap<String, Vec<&ChunkInfo>> = BTreeMap::new();
    for chunk in chunks {
        chunks_by_category
            .entry(chunk.category.clone())
            .or_default()
            .push(chunk);
    }

    // Generate chunk classes grouped by category
    for (category, category_chunks) in &chunks_by_category {
        pyi.push_str("# ");
        pyi.push_str(category);
        pyi.push_str(" Chunks\n");

        for chunk in category_chunks {
            generate_chunk_class(&mut pyi, chunk);
        }
    }

    // Type aliases section
    pyi.push_str(
        "# ============================================================================\n",
    );
    pyi.push_str("# Type Aliases and Categories\n");
    pyi.push_str(
        "# ============================================================================\n\n",
    );

    // Generate type aliases for each category
    for (category, category_chunks) in &chunks_by_category {
        let var_name = format!("{}Chunk", category);
        pyi.push_str(&format!("{} = Union[\n", var_name));

        for (i, chunk) in category_chunks.iter().enumerate() {
            pyi.push_str("    ");
            pyi.push_str(&chunk.name);
            if i < category_chunks.len() - 1 {
                pyi.push(',');
            }
            pyi.push('\n');
        }

        pyi.push_str("]\n\n");
    }

    // Generate combined type alias
    pyi.push_str("# All chunk types\n");
    pyi.push_str("AllChunks = Union[\n");
    for (i, chunk) in chunks.iter().enumerate() {
        pyi.push_str("    ");
        pyi.push_str(&chunk.name);
        if i < chunks.len() - 1 {
            pyi.push(',');
        }
        pyi.push('\n');
    }
    pyi.push_str("]\n\n");

    pyi
}

/// Generate a chunk class definition in the .pyi file
fn generate_chunk_class(pyi: &mut String, chunk: &ChunkInfo) {
    pyi.push_str(&format!("class {}(Chunk):\n", chunk.name));

    if let Some(doc_text) = &chunk.doc {
        pyi.push_str(&format!("    \"\"\"{}\"\"\"\n\n", doc_text));
    } else {
        pyi.push_str(&format!("    \"\"\"Chunk type: {}\"\"\"\n\n", chunk.name));
    }

    // Add field annotations
    for (field_name, field_type) in &chunk.fields {
        pyi.push_str(&format!("    {}: {}\n", field_name, field_type));
    }

    if !chunk.fields.is_empty() {
        pyi.push('\n');
    }

    // Generate __init__
    pyi.push_str("    def __init__(self");

    for (field_name, field_type) in &chunk.fields {
        pyi.push_str(&format!(", {}: {}", field_name, field_type));
    }

    pyi.push_str(") -> None: ...\n\n");

    // Common methods
    pyi.push_str("    def __repr__(self) -> str: ...\n");
    pyi.push_str("    def __str__(self) -> str: ...\n");
    pyi.push_str("    def to_dict(self) -> Dict[str, Any]: ...\n\n");
}

/// Convert Rust type to Python type hint
fn rust_type_to_python(ty: &Type) -> String {
    let type_str = quote!(#ty).to_string().replace(" ", "");

    match type_str.as_str() {
        "i8" | "i16" | "i32" | "i64" | "i128" | "u8" | "u16" | "u32" | "u64" | "u128" | "usize"
        | "isize" => "int".to_string(),
        "f32" | "f64" => "float".to_string(),
        "bool" => "bool".to_string(),
        "String" | "str" => "str".to_string(),
        "Vec<u8>" | "&[u8]" => "bytes".to_string(),
        s if s.starts_with("Vec<i") && s.ends_with(">") => "List[int]".to_string(),
        s if s.starts_with("Vec<") => "List[Any]".to_string(),
        s if s.starts_with("Option<") => {
            let inner = s.trim_start_matches("Option<").trim_end_matches(">");
            format!("Optional[{}]", convert_inner_type(inner))
        }
        s if s.starts_with("HashMap<") || s.starts_with("BTreeMap<") => {
            "Dict[Any, Any]".to_string()
        }
        "Uuid" => "str".to_string(),
        _ => "Any".to_string(),
    }
}

/// Convert inner type string to Python type
fn convert_inner_type(type_str: &str) -> String {
    match type_str {
        "i8" | "i16" | "i32" | "i64" | "i128" | "u8" | "u16" | "u32" | "u64" | "u128" | "usize"
        | "isize" => "int".to_string(),
        "f32" | "f64" => "float".to_string(),
        "bool" => "bool".to_string(),
        "String" | "str" => "str".to_string(),
        "Vec<u8>" | "&[u8]" => "bytes".to_string(),
        "Uuid" => "str".to_string(),
        _ => "Any".to_string(),
    }
}
