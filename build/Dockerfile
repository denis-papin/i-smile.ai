# syntax=docker/dockerfile:1
#
# AIAD site — Docker image based on a classical Ubuntu 24.04.
#
# Two stages:
#   1. builder : Ubuntu 24.04 + Rust toolchain, compiles the release binary.
#   2. runtime : plain Ubuntu 24.04 with just the binary and the static assets.
#
# Build context is the REPOSITORY ROOT (so Cargo.toml, src/ and static/ are
# reachable). From the repo root:
#
#   docker build -f build/Dockerfile -t aiad-site:latest .
#
# ---------------------------------------------------------------------------
# ---- builder ----
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Toolchain + things cargo needs to link the final binary.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install the latest stable Rust toolchain (some transitive deps, e.g.
# async-compression / compression-codecs, require a recent rustc).
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable --profile minimal

WORKDIR /app

# 1) Cache dependency compilation: copy only the manifests, build a dummy
#    binary so the dependency graph is compiled and cached as a layer.
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs \
    && cargo build --release \
    && rm -rf src

# 2) Copy the real sources and build for real. `touch` forces a rebuild of the
#    crate itself without invalidating the cached dependency layer above.
COPY src ./src
RUN touch src/main.rs && cargo build --release

# ---------------------------------------------------------------------------
# ---- runtime ----
FROM ubuntu:24.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/target/release/aiad-site /app/aiad-site
COPY static ./static

ENV AIAD_ADDR=0.0.0.0:3000 \
    AIAD_STATIC_DIR=/app/static \
    RUST_LOG=info

EXPOSE 3000
CMD ["/app/aiad-site"]
