//! Local mock demo. Replace this host boundary with verified application identity for real data.
use super::{
    document::Document,
    mock::{ExtractiveModel, HashedEmbedder},
    Rag, RagConfig,
};
use crate::ai_common::{AiError, Budget, RequestContext};
use axum::{
    extract::{rejection::JsonRejection, DefaultBodyLimit, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::post,
    Json, Router,
};
use serde::Deserialize;
use serde_json::json;
use std::{
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc,
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
                .map_err(|_| AiError::InvalidInput)?;
            for doc in docs {
                rag.ingest(doc).await?;
            }
            Ok::<_, AiError>(rag)
        })
        .await
    {
        Ok(rag) => rag,
        Err(error) => return failure(error, &id),
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
            query.top_k.unwrap_or(5),
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
