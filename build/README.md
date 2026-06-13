# build/ — Docker packaging for the AIAD site

This folder contains everything needed to build and run the project as a
Docker image based on a classical **Ubuntu 24.04**.

| File               | Purpose                                                        |
| ------------------ | ------------------------------------------------------------- |
| `Dockerfile`       | Multi-stage build (Ubuntu 24.04 + Rust → Ubuntu 24.04 runtime) |
| `.dockerignore`    | Source of truth for what to exclude from the build context     |
| `build_and_run.py` | One-shot helper: fetch repo → build image → run container      |

## Quick start (any Linux machine with git + docker + python3)

Download just the helper script and let it do everything:

```bash
curl -fsSL https://raw.githubusercontent.com/denis-papin/i-smile.ai/main/build/build_and_run.py -o build_and_run.py
python3 build_and_run.py
```

Then open <http://localhost:3000/>.

## Manual build (if you already have the repo checked out)

From the **repository root** (not from inside `build/`):

```bash
docker build -f build/Dockerfile -t aiad-site:latest .
docker run -d --name aiad-site -p 3000:3000 aiad-site:latest
```

## Helper script options

```bash
python3 build_and_run.py --port 8080      # map a different host port
python3 build_and_run.py --no-run         # build the image only
python3 build_and_run.py --no-clone --workdir .   # use the current checkout
python3 build_and_run.py --help           # all options
```

## Configuration (container env vars)

| Variable          | Default            | Meaning                     |
| ----------------- | ------------------ | --------------------------- |
| `AIAD_ADDR`       | `0.0.0.0:3000`     | bind address inside container |
| `AIAD_STATIC_DIR` | `/app/static`      | directory served as static  |
| `RUST_LOG`        | `info`             | log verbosity               |
