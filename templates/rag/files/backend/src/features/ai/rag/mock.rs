//! Offline examples only: character-hash retrieval and verbatim extraction, not a semantic LLM.
use crate::ai_common::{AiError, AiFuture, ChatModel, Embedder, ModelOutput, ModelRequest};

pub struct HashedEmbedder;

impl HashedEmbedder {
    pub fn vector(text: &str) -> Result<Vec<f32>, AiError> {
        let chars: Vec<char> = text
            .to_lowercase()
            .chars()
            .filter(|c| c.is_alphanumeric())
            .collect();
        if chars.is_empty() {
            return Err(AiError::InvalidInput);
        }
        let mut vector = vec![0.0; 256];
        for (i, c) in chars.iter().enumerate() {
            let next = chars.get(i + 1).copied().unwrap_or(*c) as u32;
            let hash = (*c as u32).wrapping_mul(16777619) ^ next;
            vector[(hash as usize) % 256] += 1.0;
        }
        Ok(vector)
    }
}

impl Embedder for HashedEmbedder {
    fn version(&self) -> &str {
        "char-hash-256-v1"
    }
    fn dimensions(&self) -> usize {
        256
    }
    fn embed<'a>(&'a self, text: &'a str) -> AiFuture<'a, Vec<f32>> {
        Box::pin(async move { Self::vector(text) })
    }
}

pub struct ExtractiveModel;

impl ChatModel for ExtractiveModel {
    fn generate<'a>(&'a self, request: ModelRequest<'a>) -> AiFuture<'a, ModelOutput> {
        Box::pin(async move {
            let first = request.context.first().ok_or(AiError::InvalidModelOutput)?;
            Ok(ModelOutput {
                text: first.chars().take(request.max_output_chars).collect(),
                used_context: vec![0],
            })
        })
    }
}
