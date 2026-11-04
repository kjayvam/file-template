use backend::ai_common::{AiError, Budget, RequestContext};
use std::time::Duration;

#[test]
fn limits_are_independent_and_exhaustion_does_not_refund_calls() {
    let mut budget = Budget::new(1, 2);
    assert_eq!(budget.reserve_model(), Ok(()));
    assert_eq!(budget.reserve_model(), Err(AiError::BudgetExceeded));
    assert_eq!(budget.reserve_embedding(), Ok(()));
    assert_eq!(budget.reserve_embedding(), Ok(()));
    assert_eq!(budget.reserve_embedding(), Err(AiError::BudgetExceeded));
    assert_eq!((budget.model_calls(), budget.embedding_calls()), (1, 2));
}

#[test]
fn identity_must_be_nonempty_and_without_control_characters() {
    assert!(RequestContext::new("", "reader", "r1", Duration::from_secs(1)).is_err());
    assert!(RequestContext::new("tenant", "a\nb", "r1", Duration::from_secs(1)).is_err());
    let context = RequestContext::new("tenant", "reader", "r1", Duration::from_secs(1)).unwrap();
    assert_eq!(
        (
            context.tenant_id(),
            context.principal_id(),
            context.request_id()
        ),
        ("tenant", "reader", "r1")
    );
}

#[test]
fn expired_context_is_rejected() {
    let context = RequestContext::new("tenant", "reader", "r1", Duration::ZERO).unwrap();
    assert_eq!(context.remaining(), Err(AiError::DeadlineExceeded));
}
