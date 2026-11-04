//! Small provider-independent contracts. No network client or runtime dependency.
pub mod budget;
pub mod context;
pub mod error;
pub mod model;

pub use budget::Budget;
pub use context::RequestContext;
pub use error::AiError;
pub use model::{AiFuture, ChatModel, Embedder, ModelOutput, ModelRequest};
