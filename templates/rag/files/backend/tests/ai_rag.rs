use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
};
use backend::{
    ai_common::{
        AiError, AiFuture, Budget, ChatModel, Embedder, ModelOutput, ModelRequest, RequestContext,
    },
    rag::{
        chunk,
        document::{AnswerStatus, Document},
        mock::{ExtractiveModel, HashedEmbedder},
        store::MemoryIndex,
        Rag, RagConfig,
    },
};
use serde_json::{json, Value};
use std::{
    sync::{
        atomic::{AtomicBool, Ordering},
        Arc, Mutex,
    },
    time::Duration,
};
use tower::ServiceExt;

fn identity(tenant: &str, reader: &str) -> RequestContext {
    RequestContext::new(tenant, reader, "test", Duration::from_secs(2)).unwrap()
}

fn doc(tenant: &str, id: &str, revision: u64, text: &str) -> Document {
    Document {
        tenant_id: tenant.into(),
        document_id: id.into(),
        revision,
        source_uri: format!("fixture://{id}"),
        readers: vec!["reader".into()],
        text: text.into(),
    }
}

fn rag() -> Rag<HashedEmbedder, ExtractiveModel> {
    Rag::new(RagConfig::default(), HashedEmbedder, ExtractiveModel).unwrap()
}

#[test]
fn unicode_chunks_have_exact_character_offsets_and_overlap() {
    let document = doc("t", "unicode", 1, "가나다라마바사");
    let chunks = chunk::split(&document, 4, 1).unwrap();
    assert_eq!(
        (
            chunks[0].text.as_str(),
            chunks[0].start_char,
            chunks[0].end_char
        ),
        ("가나다라", 0, 4)
    );
    assert_eq!(
        (
            chunks[1].text.as_str(),
            chunks[1].start_char,
            chunks[1].end_char
        ),
        ("라마바사", 3, 7)
    );
    assert!(chunk::split(&document, 3, 3).is_err());
    assert!(chunk::split(&document, 0, 0).is_err());
}

#[tokio::test]
async fn answer_cites_the_retrieved_revision_and_exact_quote() {
    let rag = rag();
    let text = "alpha log retention is seven days";
    rag.ingest(doc("t", "logs", 1, text)).await.unwrap();
    let answer = rag
        .query(&identity("t", "reader"), text, 1, &mut Budget::new(1, 1))
        .await
        .unwrap();
    assert_eq!(answer.status, AnswerStatus::Answered);
    assert_eq!(answer.text, text);
    assert_eq!(answer.citations[0].document_id, "logs");
    assert_eq!(answer.citations[0].quote, text);
    assert_eq!(answer.citations[0].revision, 1);
}

#[tokio::test]
async fn no_match_abstains_without_calling_the_model() {
    let rag = rag();
    rag.ingest(doc("t", "logs", 1, "alpha log retention is seven days"))
        .await
        .unwrap();
    let mut budget = Budget::new(0, 1);
    let answer = rag
        .query(&identity("t", "reader"), "zzzzzzzz", 1, &mut budget)
        .await
        .unwrap();
    assert_eq!(answer.status, AnswerStatus::InsufficientEvidence);
    assert!(answer.citations.is_empty());
    assert_eq!(budget.model_calls(), 0);
}

#[tokio::test]
async fn access_is_filtered_before_top_k_and_empty_acl_denies_everyone() {
    let rag = rag();
    let text = "alpha log retention is seven days";
    rag.ingest(doc("other", "a-private", 1, text))
        .await
        .unwrap();
    let mut hidden = doc("t", "b-hidden", 1, text);
    hidden.readers.clear();
    rag.ingest(hidden).await.unwrap();
    rag.ingest(doc("t", "z-visible", 1, text)).await.unwrap();
    let answer = rag
        .query(&identity("t", "reader"), text, 1, &mut Budget::new(1, 1))
        .await
        .unwrap();
    assert_eq!(answer.citations[0].document_id, "z-visible");
    let denied = rag
        .query(&identity("t", "stranger"), text, 1, &mut Budget::new(0, 1))
        .await
        .unwrap();
    assert_eq!(denied.status, AnswerStatus::InsufficientEvidence);
}

#[tokio::test]
async fn revisions_replace_old_chunks_and_deletion_removes_evidence() {
    let rag = rag();
    let original = doc("t", "logs", 1, "alpha log retention is seven days");
    assert!(rag.ingest(original.clone()).await.unwrap());
    assert!(!rag.ingest(original.clone()).await.unwrap());
    assert_eq!(
        rag.ingest(doc("t", "logs", 1, "different text")).await,
        Err(AiError::RevisionConflict)
    );
    let updated = doc("t", "logs", 2, "alpha log retention is fourteen days");
    rag.ingest(updated.clone()).await.unwrap();
    assert_eq!(rag.ingest(original).await, Err(AiError::RevisionConflict));
    let answer = rag
        .query(
            &identity("t", "reader"),
            &updated.text,
            1,
            &mut Budget::new(1, 1),
        )
        .await
        .unwrap();
    assert_eq!(answer.citations[0].revision, 2);
    assert!(answer.text.contains("fourteen"));
    assert!(rag.index().delete("t", "logs").unwrap());
    let answer = rag
        .query(
            &identity("t", "reader"),
            &updated.text,
            1,
            &mut Budget::new(0, 1),
        )
        .await
        .unwrap();
    assert_eq!(answer.status, AnswerStatus::InsufficientEvidence);
}

struct RevokingModel {
    index: Arc<Mutex<Option<Arc<MemoryIndex>>>>,
}
impl ChatModel for RevokingModel {
    fn generate<'a>(&'a self, request: ModelRequest<'a>) -> AiFuture<'a, ModelOutput> {
        Box::pin(async move {
            self.index
                .lock()
                .unwrap()
                .as_ref()
                .unwrap()
                .set_readers("t", "logs", vec![])?;
            Ok(ModelOutput {
                text: request.context[0].into(),
                used_context: vec![0],
            })
        })
    }
}

#[tokio::test]
async fn revocation_during_generation_prevents_returning_stale_context() {
    let holder = Arc::new(Mutex::new(None));
    let rag = Rag::new(
        RagConfig::default(),
        HashedEmbedder,
        RevokingModel {
            index: holder.clone(),
        },
    )
    .unwrap();
    *holder.lock().unwrap() = Some(rag.index());
    rag.ingest(doc("t", "logs", 1, "alpha log retention"))
        .await
        .unwrap();
    let result = rag
        .query(
            &identity("t", "reader"),
            "alpha log retention",
            1,
            &mut Budget::new(1, 1),
        )
        .await;
    assert_eq!(result.unwrap_err(), AiError::EvidenceChanged);
}

struct BadModel;
impl ChatModel for BadModel {
    fn generate<'a>(&'a self, _request: ModelRequest<'a>) -> AiFuture<'a, ModelOutput> {
        Box::pin(async {
            Ok(ModelOutput {
                text: "invented source".into(),
                used_context: vec![999],
            })
        })
    }
}

#[tokio::test]
async fn invented_citation_index_is_rejected() {
    let rag = Rag::new(RagConfig::default(), HashedEmbedder, BadModel).unwrap();
    rag.ingest(doc("t", "logs", 1, "alpha log retention"))
        .await
        .unwrap();
    assert_eq!(
        rag.query(
            &identity("t", "reader"),
            "alpha log retention",
            1,
            &mut Budget::new(1, 1)
        )
        .await
        .unwrap_err(),
        AiError::InvalidModelOutput
    );
}

#[tokio::test]
async fn limits_and_invalid_input_fail_before_unapproved_calls() {
    let rag = rag();
    rag.ingest(doc("t", "logs", 1, "alpha log retention"))
        .await
        .unwrap();
    assert_eq!(
        rag.query(
            &identity("t", "reader"),
            "alpha log retention",
            1,
            &mut Budget::new(0, 1)
        )
        .await
        .unwrap_err(),
        AiError::BudgetExceeded
    );
    assert_eq!(
        rag.query(&identity("t", "reader"), "alpha", 1, &mut Budget::new(1, 0))
            .await
            .unwrap_err(),
        AiError::BudgetExceeded
    );
    for (question, k) in [("", 1), ("alpha", 0), ("alpha", 6)] {
        assert_eq!(
            rag.query(
                &identity("t", "reader"),
                question,
                k,
                &mut Budget::new(1, 1)
            )
            .await
            .unwrap_err(),
            AiError::InvalidInput
        );
    }
}

struct PendingEmbedder;
impl Embedder for PendingEmbedder {
    fn version(&self) -> &str {
        "pending-v1"
    }
    fn dimensions(&self) -> usize {
        2
    }
    fn embed<'a>(&'a self, _text: &'a str) -> AiFuture<'a, Vec<f32>> {
        Box::pin(std::future::pending())
    }
}

#[tokio::test]
async fn deadline_stops_a_pending_provider_future() {
    let rag = Rag::new(RagConfig::default(), PendingEmbedder, ExtractiveModel).unwrap();
    let context = RequestContext::new("t", "reader", "timeout", Duration::from_millis(10)).unwrap();
    assert_eq!(
        rag.query(&context, "alpha", 1, &mut Budget::new(1, 1))
            .await
            .unwrap_err(),
        AiError::DeadlineExceeded
    );
}

struct BadEmbedder {
    changed: Arc<AtomicBool>,
}
impl Embedder for BadEmbedder {
    fn version(&self) -> &str {
        if self.changed.load(Ordering::SeqCst) {
            "v2"
        } else {
            "v1"
        }
    }
    fn dimensions(&self) -> usize {
        2
    }
    fn embed<'a>(&'a self, _text: &'a str) -> AiFuture<'a, Vec<f32>> {
        Box::pin(async { Ok(vec![f32::NAN, 1.0]) })
    }
}

#[tokio::test]
async fn invalid_vectors_and_changed_embedding_versions_are_rejected() {
    let changed = Arc::new(AtomicBool::new(false));
    let rag = Rag::new(
        RagConfig::default(),
        BadEmbedder {
            changed: changed.clone(),
        },
        ExtractiveModel,
    )
    .unwrap();
    assert_eq!(
        rag.ingest(doc("t", "x", 1, "alpha")).await,
        Err(AiError::InvalidEmbedding)
    );
    changed.store(true, Ordering::SeqCst);
    assert_eq!(
        rag.query(&identity("t", "reader"), "alpha", 1, &mut Budget::new(1, 1))
            .await
            .unwrap_err(),
        AiError::InvalidEmbedding
    );
    assert!(backend::rag::store::validate_vector(&[1.0], 2).is_err());
    assert!(backend::rag::store::validate_vector(&[0.0, 0.0], 2).is_err());
}

async fn api(body: Value) -> (StatusCode, Value) {
    let response = backend::app()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/ai/v1/query")
                .header("content-type", "application/json")
                .body(Body::from(body.to_string()))
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let body = to_bytes(response.into_body(), 32_768).await.unwrap();
    (status, serde_json::from_slice(&body).unwrap())
}

#[tokio::test]
async fn http_demo_is_wired_and_returns_mock_citations() {
    let (status, value) = api(json!({"question":"로그 보관 기간은 7일입니다.","top_k":1})).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(value["data"]["status"], "answered");
    assert_eq!(value["data"]["citations"][0]["document_id"], "logging");
    assert_eq!(value["meta"]["mock"], true);
    assert!(!value.to_string().contains("PRIVATE_FIXTURE_SECRET"));
}

#[tokio::test]
async fn http_rejects_identity_spoofing_bad_json_fields_and_large_bodies() {
    for body in [
        json!({"question":"x","tenant_id":"private"}),
        json!({"question":""}),
        json!({"question":"x","top_k":0}),
        json!({}),
    ] {
        let (status, value) = api(body).await;
        assert_eq!(status, StatusCode::BAD_REQUEST);
        assert_eq!(value["success"], false);
    }
    assert_eq!(
        api(json!({"question":"x".repeat(17000)})).await.0,
        StatusCode::PAYLOAD_TOO_LARGE
    );
}
