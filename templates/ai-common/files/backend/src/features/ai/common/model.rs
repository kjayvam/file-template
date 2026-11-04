use super::AiError;
use std::{future::Future, pin::Pin};

pub type AiFuture<'a, T> = Pin<Box<dyn Future<Output = Result<T, AiError>> + Send + 'a>>;

pub trait Embedder: Send + Sync {
    fn version(&self) -> &str;
    fn dimensions(&self) -> usize;
    fn embed<'a>(&'a self, text: &'a str) -> AiFuture<'a, Vec<f32>>;
}

pub struct ModelRequest<'a> {
    pub instruction: &'a str,
    pub question: &'a str,
    pub context: &'a [&'a str],
    pub max_output_chars: usize,
}

pub struct ModelOutput {
    pub text: String,
    /// Zero-based indices into the supplied context, validated by the RAG layer.
    pub used_context: Vec<usize>,
}

pub trait ChatModel: Send + Sync {
    fn generate<'a>(&'a self, request: ModelRequest<'a>) -> AiFuture<'a, ModelOutput>;
}
