use backend::app;
use std::net::SocketAddr;
use tracing::info;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let port =
        port_from(std::env::var("PORT").ok().as_deref()).unwrap_or_else(|error| panic!("{error}"));

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .unwrap_or_else(|error| panic!("{addr} 포트를 열 수 없습니다: {error}"));
    info!("Backend server listening on {}", addr);

    axum::serve(listener, app())
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("서버 실행 중 오류가 발생했습니다");
}

/// PORT가 없으면 8080을 쓰고, 잘못된 값은 다른 포트로 조용히 바꾸지 않고 시작을 멈춥니다.
fn port_from(value: Option<&str>) -> Result<u16, String> {
    match value {
        None => Ok(8080),
        Some(text) => text
            .trim()
            .parse::<u16>()
            .map_err(|_| format!("PORT 값이 올바르지 않습니다: {text:?} (0~65535 정수)")),
    }
}

/// Ctrl+C 또는 SIGTERM(docker stop)을 받으면 진행 중인 요청을 마치고 종료합니다.
/// 컨테이너의 PID 1은 기본 시그널 처리가 없으므로 직접 처리하지 않으면 강제 종료까지 기다립니다.
async fn shutdown_signal() {
    let ctrl_c = async {
        tokio::signal::ctrl_c()
            .await
            .expect("Ctrl+C 처리기를 등록할 수 없습니다");
    };

    #[cfg(unix)]
    let terminate = async {
        tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
            .expect("SIGTERM 처리기를 등록할 수 없습니다")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
    info!("종료 신호를 받아 서버를 정리합니다");
}

#[cfg(test)]
mod tests {
    use super::port_from;

    #[test]
    fn port_defaults_to_8080_and_rejects_invalid_values() {
        assert_eq!(port_from(None), Ok(8080));
        assert_eq!(port_from(Some("3000")), Ok(3000));
        assert!(port_from(Some("abc")).is_err());
        assert!(port_from(Some("70000")).is_err());
        assert!(port_from(Some("")).is_err());
    }
}
