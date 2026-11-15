//! Local mock demo. Replace this host boundary with verified application identity for real data.
use super::{
    Rag, RagConfig,
    document::Document,
    mock::{ExtractiveModel, HashedEmbedder},
};
use crate::ai_common::{AiError, Budget, RequestContext};
use axum::{
    Json, Router,
    extract::{DefaultBodyLimit, State, rejection::JsonRejection},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::post,
};
use serde::Deserialize;
use serde_json::json;
use std::{
    sync::{
        Arc,
        atomic::{AtomicU64, Ordering},
    },
    time::Duration,
};
use tokio::sync::OnceCell;

type Demo = Rag<HashedEmbedder, ExtractiveModel>;
static REQUEST: AtomicU64 = AtomicU64::new(1);

pub fn demo_router() -> Router {
    Router::new()
        .route("/api/ai/v1/query", post(query))
        .layer(DefaultBodyLimit::max(16_384))
        .with_state(Arc::new(OnceCell::<Demo>::new()))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Query {
    question: String,
    top_k: Option<usize>,
}

fn failure(error: AiError, request_id: &str) -> Response {
    let status = match error {
        AiError::InvalidInput => StatusCode::BAD_REQUEST,
        AiError::BudgetExceeded => StatusCode::TOO_MANY_REQUESTS,
        AiError::DeadlineExceeded => StatusCode::GATEWAY_TIMEOUT,
        AiError::EvidenceChanged | AiError::RevisionConflict => StatusCode::CONFLICT,
        // The in-memory store failing is an internal error, not a provider outage.
        AiError::StoreUnavailable => StatusCode::INTERNAL_SERVER_ERROR,
        _ => StatusCode::BAD_GATEWAY,
    };
    (
        status,
        Json(json!({"success":false,"error":{"code":error.code()},"meta":{"trace_id":request_id}})),
    )
        .into_response()
}

async fn query(
    State(cell): State<Arc<OnceCell<Demo>>>,
    input: Result<Json<Query>, JsonRejection>,
) -> Response {
    let id = format!("demo-{}", REQUEST.fetch_add(1, Ordering::Relaxed));
    let query = match input {
        Ok(Json(query)) => query,
        Err(rejection) => {
            if rejection.status() == StatusCode::PAYLOAD_TOO_LARGE {
                return (StatusCode::PAYLOAD_TOO_LARGE, Json(json!({"success":false,"error":{"code":"payload_too_large"},"meta":{"trace_id":id}}))).into_response();
            }
            return failure(AiError::InvalidInput, &id);
        }
    };
    let rag = match cell
        .get_or_try_init(|| async {
            let rag = Rag::new(RagConfig::default(), HashedEmbedder, ExtractiveModel)?;
            let docs: Vec<Document> = serde_json::from_str(include_str!("demo/corpus.json"))
                .map_err(|_| AiError::StoreUnavailable)?;
            for doc in docs {
                rag.ingest(doc).await?;
            }
            Ok::<_, AiError>(rag)
        })
        .await
    {
        Ok(rag) => rag,
        // Building the bundled demo index never depends on the request, so any failure is internal (500).
        Err(_) => return failure(AiError::StoreUnavailable, &id),
    };
    let context = match RequestContext::new("demo", "reader", &id, Duration::from_secs(5)) {
        Ok(context) => context,
        Err(error) => return failure(error, &id),
    };
    let mut budget = Budget::new(1, 1);
    match rag
        .query(
            &context,
            &query.question,
            // An omitted top_k follows the configured maximum instead of a separate constant.
            query.top_k.unwrap_or(rag.config().max_top_k),
            &mut budget,
        )
        .await
    {
        Ok(answer) => Json(
            json!({"success":true,"data":answer,"meta":{"trace_id":id,"mock":true,
            "calls":{"model":budget.model_calls(),"embedding":budget.embedding_calls()}}}),
        )
        .into_response(),
        Err(error) => failure(error, &id),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn failure_separates_internal_store_errors_from_provider_errors() {
        let status = |error| failure(error, "t").status();
        assert_eq!(
            status(AiError::StoreUnavailable),
            StatusCode::INTERNAL_SERVER_ERROR
        );
        assert_eq!(
            status(AiError::ProviderUnavailable),
            StatusCode::BAD_GATEWAY
        );
        assert_eq!(status(AiError::InvalidModelOutput), StatusCode::BAD_GATEWAY);
    }
}
