use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Document {
    pub tenant_id: String,
    pub document_id: String,
    pub revision: u64,
    pub source_uri: String,
    pub readers: Vec<String>,
    pub text: String,
}

#[derive(Clone, Debug)]
pub struct Chunk {
    pub document: std::sync::Arc<Document>,
    pub chunk_id: String,
    pub start_char: usize,
    pub end_char: usize,
    pub text: String,
    pub vector: Vec<f32>,
}

#[derive(Debug, Serialize)]
pub struct Citation {
    pub document_id: String,
    pub revision: u64,
    pub chunk_id: String,
    pub source_uri: String,
    pub start_char: usize,
    pub end_char: usize,
    pub quote: String,
}

#[derive(Debug, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum AnswerStatus {
    Answered,
    InsufficientEvidence,
}

#[derive(Debug, Serialize)]
pub struct Answer {
    pub status: AnswerStatus,
    pub text: String,
    pub citations: Vec<Citation>,
}
