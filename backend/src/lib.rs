use axum::{Json, Router, routing::get};
use serde_json::{Value, json};

pub fn app() -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/api/v1/health", get(health_check))
}

async fn health_check() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "service": "backend",
        "timestamp": chrono::Utc::now().to_rfc3339()
    }))
}
