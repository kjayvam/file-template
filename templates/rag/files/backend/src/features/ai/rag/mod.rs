//! In-memory RAG building blocks; live model, persistence and authentication are host adapters.
pub mod chunk;
pub mod document;
pub mod http;
pub mod mock;
pub mod store;

use crate::ai_common::{AiError, Budget, ChatModel, Embedder, ModelRequest, RequestContext};
use document::{Answer, AnswerStatus, Citation, Document};
use std::{future::Future, sync::Arc, time::Duration};
use store::{validate_vector, MemoryIndex};

#[derive(Clone)]
pub struct RagConfig {
    pub chunk_chars: usize,
    pub overlap_chars: usize,
    pub minimum_score: f64,
    pub max_top_k: usize,
    pub max_question_chars: usize,
    pub max_output_chars: usize,
}

impl Default for RagConfig {
    fn default() -> Self {
        Self {
            chunk_chars: 800,
            overlap_chars: 100,
            minimum_score: 0.2,
            max_top_k: 5,
            max_question_chars: 4000,
            max_output_chars: 2000,
        }
    }
}

pub struct Rag<E, M> {
    config: RagConfig,
    embedder: E,
    model: M,
    index: Arc<MemoryIndex>,
    embedding_version: String,
    dimensions: usize,
}

async fn bounded<T>(
    context: &RequestContext,
    future: impl Future<Output = Result<T, AiError>>,
) -> Result<T, AiError> {
    let result = tokio::time::timeout(context.remaining()?, future)
        .await
        .map_err(|_| AiError::DeadlineExceeded)??;
    context.remaining()?;
    Ok(result)
}

impl<E: Embedder, M: ChatModel> Rag<E, M> {
    pub fn new(config: RagConfig, embedder: E, model: M) -> Result<Self, AiError> {
        if config.chunk_chars == 0
            || config.chunk_chars > 50_000
            || config.overlap_chars >= config.chunk_chars
            || config.max_top_k == 0
            || config.max_top_k > 20
            || config.max_question_chars == 0
            || config.max_output_chars == 0
            || !config.minimum_score.is_finite()
            || !(0.0..=1.0).contains(&config.minimum_score)
            || embedder.dimensions() == 0
            || embedder.dimensions() > 4096
            || embedder.version().is_empty()
        {
            return Err(AiError::InvalidInput);
        }
        let embedding_version = embedder.version().to_owned();
        let dimensions = embedder.dimensions();
        Ok(Self {
            config,
            embedder,
            model,
            index: Arc::new(MemoryIndex::default()),
            embedding_version,
            dimensions,
        })
    }

    pub fn index(&self) -> Arc<MemoryIndex> {
        self.index.clone()
    }

    pub fn config(&self) -> &RagConfig {
        &self.config
    }

    fn check_embedding_version(&self) -> Result<(), AiError> {
        if self.embedder.version() != self.embedding_version
            || self.embedder.dimensions() != self.dimensions
        {
            return Err(AiError::InvalidEmbedding);
        }
        Ok(())
    }

    /// Trusted host ingestion. Input text must already be normalized by the host.
    pub async fn ingest(&self, document: Document) -> Result<bool, AiError> {
        self.check_embedding_version()?;
        let mut chunks = chunk::split(
            &document,
            self.config.chunk_chars,
            self.config.overlap_chars,
        )?;
        for chunk in &mut chunks {
            chunk.vector =
                tokio::time::timeout(Duration::from_secs(5), self.embedder.embed(&chunk.text))
                    .await
                    .map_err(|_| AiError::DeadlineExceeded)??;
            validate_vector(&chunk.vector, self.dimensions)?;
        }
        self.check_embedding_version()?;
        self.index.put(document, chunks)
    }

    pub async fn query(
        &self,
        context: &RequestContext,
        question: &str,
        top_k: usize,
        budget: &mut Budget,
    ) -> Result<Answer, AiError> {
        if question.trim().is_empty()
            || question.chars().count() > self.config.max_question_chars
            || top_k == 0
            || top_k > self.config.max_top_k
        {
            return Err(AiError::InvalidInput);
        }
        context.remaining()?;
        self.check_embedding_version()?;
        budget.reserve_embedding()?;
        let vector = bounded(context, self.embedder.embed(question)).await?;
        self.check_embedding_version()?;
        validate_vector(&vector, self.dimensions)?;
        let chunks = self
            .index
            .search(context, &vector, top_k, self.config.minimum_score)?;
        if chunks.is_empty() {
            return Ok(Answer {
                status: AnswerStatus::InsufficientEvidence,
                text: String::new(),
                citations: Vec::new(),
            });
        }
        let passages: Vec<&str> = chunks.iter().map(|c| c.text.as_str()).collect();
        budget.reserve_model()?;
        let output = bounded(
            context,
            self.model.generate(ModelRequest {
                instruction: include_str!("prompts/answer.v1.md"),
                question,
                context: &passages,
                max_output_chars: self.config.max_output_chars,
            }),
        )
        .await?;
        if output.text.trim().is_empty()
            || output.text.chars().count() > self.config.max_output_chars
            || output.used_context.is_empty()
            || output.used_context.iter().any(|i| *i >= chunks.len())
        {
            return Err(AiError::InvalidModelOutput);
        }
        self.index.validate_evidence(context, &chunks)?;
        let mut indices = output.used_context;
        indices.sort_unstable();
        indices.dedup();
        let citations = indices
            .iter()
            .map(|i| {
                let c = &chunks[*i];
                Citation {
                    document_id: c.document.document_id.clone(),
                    revision: c.document.revision,
                    chunk_id: c.chunk_id.clone(),
                    source_uri: c.document.source_uri.clone(),
                    start_char: c.start_char,
                    end_char: c.end_char,
                    quote: c.text.clone(),
                }
            })
            .collect();
        Ok(Answer {
            status: AnswerStatus::Answered,
            text: output.text,
            citations,
        })
    }
}
