use super::document::{Chunk, Document};
use crate::ai_common::{AiError, RequestContext};
use std::{collections::HashMap, sync::RwLock};

struct Entry {
    document: Document,
    chunks: Vec<Chunk>,
}

#[derive(Default)]
pub struct MemoryIndex {
    entries: RwLock<HashMap<(String, String), Entry>>,
}

fn visible(document: &Document, context: &RequestContext) -> bool {
    document.tenant_id == context.tenant_id()
        && document.readers.iter().any(|p| p == context.principal_id())
}

pub fn validate_vector(vector: &[f32], dimensions: usize) -> Result<(), AiError> {
    if dimensions == 0
        || vector.len() != dimensions
        || vector.iter().any(|v| !v.is_finite())
        || vector.iter().all(|v| *v == 0.0)
    {
        return Err(AiError::InvalidEmbedding);
    }
    Ok(())
}

fn cosine(a: &[f32], b: &[f32]) -> f64 {
    let dot: f64 = a.iter().zip(b).map(|(a, b)| *a as f64 * *b as f64).sum();
    let norm = |v: &[f32]| v.iter().map(|x| (*x as f64).powi(2)).sum::<f64>().sqrt();
    dot / (norm(a) * norm(b))
}

impl MemoryIndex {
    /// Host-only ingestion. A fixed index signature prevents mixed embedding/chunk versions.
    pub(super) fn put(&self, document: Document, chunks: Vec<Chunk>) -> Result<bool, AiError> {
        let mut entries = self
            .entries
            .write()
            .map_err(|_| AiError::StoreUnavailable)?;
        let key = (document.tenant_id.clone(), document.document_id.clone());
        if let Some(old) = entries.get(&key) {
            if old.document == document {
                return Ok(false);
            }
            if document.revision <= old.document.revision {
                return Err(AiError::RevisionConflict);
            }
        }
        entries.insert(key, Entry { document, chunks });
        Ok(true)
    }

    pub fn delete(&self, tenant: &str, id: &str) -> Result<bool, AiError> {
        Ok(self
            .entries
            .write()
            .map_err(|_| AiError::StoreUnavailable)?
            .remove(&(tenant.into(), id.into()))
            .is_some())
    }

    pub fn set_readers(&self, tenant: &str, id: &str, readers: Vec<String>) -> Result<(), AiError> {
        let mut entries = self
            .entries
            .write()
            .map_err(|_| AiError::StoreUnavailable)?;
        let entry = entries
            .get_mut(&(tenant.into(), id.into()))
            .ok_or(AiError::InvalidInput)?;
        entry.document.readers = readers;
        Ok(())
    }

    pub fn search(
        &self,
        context: &RequestContext,
        vector: &[f32],
        top_k: usize,
        minimum: f64,
    ) -> Result<Vec<Chunk>, AiError> {
        let entries = self.entries.read().map_err(|_| AiError::StoreUnavailable)?;
        // Restrict the candidate set before scoring and top-k selection.
        let mut ranked: Vec<_> = entries
            .values()
            .filter(|e| visible(&e.document, context))
            .flat_map(|e| e.chunks.iter())
            .map(|c| (cosine(vector, &c.vector), c))
            .filter(|(score, _)| score.is_finite() && *score >= minimum)
            .collect();
        ranked.sort_by(|(a, ca), (b, cb)| {
            b.total_cmp(a)
                .then(ca.document.document_id.cmp(&cb.document.document_id))
                .then(ca.start_char.cmp(&cb.start_char))
        });
        Ok(ranked
            .into_iter()
            .take(top_k)
            .map(|(_, c)| c.clone())
            .collect())
    }

    /// Recheck all supplied context, including context the model did not cite.
    pub fn validate_evidence(
        &self,
        context: &RequestContext,
        chunks: &[Chunk],
    ) -> Result<(), AiError> {
        let entries = self.entries.read().map_err(|_| AiError::StoreUnavailable)?;
        for chunk in chunks {
            let key = (
                chunk.document.tenant_id.clone(),
                chunk.document.document_id.clone(),
            );
            let entry = entries.get(&key).ok_or(AiError::EvidenceChanged)?;
            if !visible(&entry.document, context)
                || entry.document.revision != chunk.document.revision
                || !entry
                    .chunks
                    .iter()
                    .any(|c| c.chunk_id == chunk.chunk_id && c.text == chunk.text)
            {
                return Err(AiError::EvidenceChanged);
            }
        }
        Ok(())
    }
}
