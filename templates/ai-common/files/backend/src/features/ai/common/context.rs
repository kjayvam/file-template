use super::AiError;
use std::time::{Duration, Instant};

/// Constructed by the host's trusted identity boundary, never from a query body.
#[derive(Clone, Debug)]
pub struct RequestContext {
    tenant_id: String,
    principal_id: String,
    request_id: String,
    deadline: Instant,
}

impl RequestContext {
    pub fn new(
        tenant: &str,
        principal: &str,
        request: &str,
        timeout: Duration,
    ) -> Result<Self, AiError> {
        if [tenant, principal, request]
            .iter()
            .any(|s| s.trim().is_empty() || s.len() > 128 || s.chars().any(char::is_control))
        {
            return Err(AiError::InvalidInput);
        }
        let deadline = Instant::now()
            .checked_add(timeout)
            .ok_or(AiError::InvalidInput)?;
        Ok(Self {
            tenant_id: tenant.into(),
            principal_id: principal.into(),
            request_id: request.into(),
            deadline,
        })
    }

    pub fn tenant_id(&self) -> &str {
        &self.tenant_id
    }
    pub fn principal_id(&self) -> &str {
        &self.principal_id
    }
    pub fn request_id(&self) -> &str {
        &self.request_id
    }

    pub fn remaining(&self) -> Result<Duration, AiError> {
        self.deadline
            .checked_duration_since(Instant::now())
            .filter(|d| !d.is_zero())
            .ok_or(AiError::DeadlineExceeded)
    }
}
