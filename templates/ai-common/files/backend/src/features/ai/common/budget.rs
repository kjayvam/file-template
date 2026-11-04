use super::AiError;

/// Call-count limits, not monetary accounting. Reservations are not refunded on failure.
#[derive(Debug)]
pub struct Budget {
    model_limit: usize,
    embedding_limit: usize,
    model_calls: usize,
    embedding_calls: usize,
}

impl Budget {
    pub fn new(model_limit: usize, embedding_limit: usize) -> Self {
        Self {
            model_limit,
            embedding_limit,
            model_calls: 0,
            embedding_calls: 0,
        }
    }

    pub fn reserve_model(&mut self) -> Result<(), AiError> {
        if self.model_calls >= self.model_limit {
            return Err(AiError::BudgetExceeded);
        }
        self.model_calls += 1;
        Ok(())
    }

    pub fn reserve_embedding(&mut self) -> Result<(), AiError> {
        if self.embedding_calls >= self.embedding_limit {
            return Err(AiError::BudgetExceeded);
        }
        self.embedding_calls += 1;
        Ok(())
    }

    pub fn model_calls(&self) -> usize {
        self.model_calls
    }
    pub fn embedding_calls(&self) -> usize {
        self.embedding_calls
    }
}
