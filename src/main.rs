//! AIAD — AI Assisted Development
//!
//! Minimal Axum server that exposes the commercial website as static assets.
//!
//! Routes:
//!   GET  /            -> static/index.html
//!   GET  /healthz     -> 200 "ok"
//!   GET  /*           -> any file under ./static (CSS, JS, images, ...)
//!
//! Configuration (env vars):
//!   AIAD_ADDR       default "0.0.0.0:3000"
//!   AIAD_STATIC_DIR default "static"
//!   RUST_LOG        default "info,tower_http=info"

use std::{net::SocketAddr, path::PathBuf};

use axum::{
    http::{HeaderName, HeaderValue, StatusCode},
    routing::get,
    Router,
};
use tower_http::{
    compression::CompressionLayer,
    services::{ServeDir, ServeFile},
    set_header::SetResponseHeaderLayer,
    trace::TraceLayer,
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

#[tokio::main]
async fn main() {
    init_tracing();

    let static_dir: PathBuf = std::env::var("AIAD_STATIC_DIR")
        .unwrap_or_else(|_| "static".to_string())
        .into();

    if !static_dir.exists() {
        eprintln!(
            "warning: static directory '{}' does not exist (cwd = {:?})",
            static_dir.display(),
            std::env::current_dir().ok()
        );
    }

    let index_file = static_dir.join("index.html");

    // ServeDir handles every file under ./static; on miss, fall back to index.html
    // so SPA-style links still work.
    let serve_dir =
        ServeDir::new(&static_dir).not_found_service(ServeFile::new(index_file.clone()));

    let app = Router::new()
        .route("/healthz", get(healthz))
        .fallback_service(serve_dir)
        // Compress text payloads (HTML/CSS/JS).
        .layer(CompressionLayer::new())
        // A polite default Cache-Control for static assets (override per-asset later if needed).
        .layer(SetResponseHeaderLayer::if_not_present(
            HeaderName::from_static("cache-control"),
            HeaderValue::from_static("public, max-age=300"),
        ))
        // Basic request tracing.
        .layer(TraceLayer::new_for_http());

    let addr: SocketAddr = std::env::var("AIAD_ADDR")
        .unwrap_or_else(|_| "0.0.0.0:3000".to_string())
        .parse()
        .expect("AIAD_ADDR must be a valid socket address, e.g. 0.0.0.0:3000");

    tracing::info!(%addr, static_dir = %static_dir.display(), "AIAD site listening");

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("failed to bind TCP listener");

    axum::serve(listener, app)
        .await
        .expect("axum server error");
}

async fn healthz() -> (StatusCode, &'static str) {
    (StatusCode::OK, "ok")
}

fn init_tracing() {
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info,tower_http=info,aiad_site=info"));

    tracing_subscriber::registry()
        .with(filter)
        .with(tracing_subscriber::fmt::layer().with_target(false))
        .init();
}
