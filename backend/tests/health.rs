use axum::{
    body::{to_bytes, Body},
    http::{header::CONTENT_TYPE, Method, Request, StatusCode},
};
use backend::app;
use serde_json::Value;
use tower::ServiceExt;

async fn assert_health_response(path: &str) {
    let before = chrono::Utc::now();
    let response = app()
        .oneshot(Request::builder().uri(path).body(Body::empty()).unwrap())
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    assert_eq!(response.headers()[CONTENT_TYPE], "application/json");

    let body = to_bytes(response.into_body(), 4096).await.unwrap();
    let json: Value = serde_json::from_slice(&body).unwrap();
    assert_eq!(json["status"], "ok");
    assert_eq!(json["service"], "backend");
    let timestamp = chrono::DateTime::parse_from_rfc3339(json["timestamp"].as_str().unwrap())
        .unwrap()
        .with_timezone(&chrono::Utc);
    assert!(timestamp >= before && timestamp <= chrono::Utc::now());
}

#[tokio::test]
async fn health_endpoint_returns_service_status() {
    assert_health_response("/health").await;
}

#[tokio::test]
async fn versioned_health_endpoint_returns_service_status() {
    assert_health_response("/api/v1/health").await;
}

#[tokio::test]
async fn unknown_route_returns_not_found() {
    let response = app()
        .oneshot(
            Request::builder()
                .uri("/api/v1/missing")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn health_endpoint_rejects_post() {
    let response = app()
        .oneshot(
            Request::builder()
                .method(Method::POST)
                .uri("/api/v1/health")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(response.status(), StatusCode::METHOD_NOT_ALLOWED);
}
