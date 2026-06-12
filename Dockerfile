# ---- builder ----
FROM rust:1.82-slim AS builder
WORKDIR /app

# Cache dependencies
COPY Cargo.toml ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Real sources
COPY src ./src
RUN touch src/main.rs && cargo build --release

# ---- runtime ----
FROM debian:bookworm-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/aiad-site /app/aiad-site
COPY static ./static

ENV AIAD_ADDR=0.0.0.0:3000 \
    AIAD_STATIC_DIR=/app/static \
    RUST_LOG=info

EXPOSE 3000
CMD ["/app/aiad-site"]
