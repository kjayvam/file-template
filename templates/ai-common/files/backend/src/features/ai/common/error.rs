use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AiError {
    InvalidInput,
    InvalidEmbedding,
    InvalidModelOutput,
    BudgetExceeded,
    DeadlineExceeded,
    RevisionConflict,
    EvidenceChanged,
    StoreUnavailable,
    ProviderUnavailable,
}

impl AiError {
    pub fn code(self) -> &'static str {
        match self {
            Self::InvalidInput => "invalid_input",
            Self::InvalidEmbedding => "invalid_embedding",
            Self::InvalidModelOutput => "invalid_model_output",
            Self::BudgetExceeded => "budget_exceeded",
            Self::DeadlineExceeded => "deadline_exceeded",
            Self::RevisionConflict => "revision_conflict",
            Self::EvidenceChanged => "evidence_changed",
            Self::StoreUnavailable => "store_unavailable",
            Self::ProviderUnavailable => "provider_unavailable",
        }
    }
}

impl fmt::Display for AiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.code())
    }
}

impl std::error::Error for AiError {}
