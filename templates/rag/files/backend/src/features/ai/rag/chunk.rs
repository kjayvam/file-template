use super::document::{Chunk, Document};
use crate::ai_common::AiError;

/// Offsets count Unicode scalar values in the original normalized text, not bytes.
pub fn split(document: &Document, size: usize, overlap: usize) -> Result<Vec<Chunk>, AiError> {
    if size == 0 || overlap >= size {
        return Err(AiError::InvalidInput);
    }
    let chars: Vec<char> = document.text.chars().collect();
    if chars.is_empty()
        || chars.len() > 50_000
        || document.revision == 0
        || [
            &document.tenant_id,
            &document.document_id,
            &document.source_uri,
        ]
        .iter()
        .any(|s| s.trim().is_empty())
        || document.readers.iter().any(|s| s.trim().is_empty())
    {
        return Err(AiError::InvalidInput);
    }
    let mut chunks = Vec::new();
    if chars.len().div_ceil(size - overlap) > 256 {
        return Err(AiError::InvalidInput);
    }
    let shared = std::sync::Arc::new(document.clone());
    let mut start: usize = 0;
    loop {
        let end = start.saturating_add(size).min(chars.len());
        chunks.push(Chunk {
            document: shared.clone(),
            chunk_id: format!("{}:{}:{}", document.document_id, document.revision, start),
            start_char: start,
            end_char: end,
            text: chars[start..end].iter().collect(),
            vector: Vec::new(),
        });
        if end == chars.len() {
            break;
        }
        start = end - overlap;
    }
    Ok(chunks)
}
