#!/usr/bin/env python3
"""
Fetch the AIAD site project, build its Docker image and run the container.

Works on any Linux machine that has `git`, `docker` and Python 3 installed.
No third-party Python packages required (standard library only).

Typical usage
-------------
    # clone (or update) the repo, build the image and run it on port 3000
    python3 build_and_run.py

    # pick a different host port
    python3 build_and_run.py --port 8080

    # build only, do not run
    python3 build_and_run.py --no-run

    # use an already-cloned checkout instead of cloning
    python3 build_and_run.py --workdir /path/to/i-smile.ai --no-clone

Once running, open http://localhost:<port>/  (health check: /healthz).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

# --------------------------------------------------------------------------- #
# Defaults
# --------------------------------------------------------------------------- #
DEFAULT_REPO = "https://github.com/denis-papin/i-smile.ai.git"
DEFAULT_BRANCH = "main"
DEFAULT_WORKDIR = "i-smile.ai"      # local clone directory
DEFAULT_IMAGE = "i-smile.ai:latest"
DEFAULT_CONTAINER = "i-smile.ai"
DEFAULT_PORT = 3000                 # host port -> container 3000


def run(cmd: list[str], **kwargs) -> None:
    """Run a command, streaming output; abort the script on failure."""
    print(f"\n$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True, **kwargs)


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def ensure_prerequisites() -> None:
    missing = [t for t in ("git", "docker") if not have(t)]
    if missing:
        sys.exit(f"error: required tool(s) not found on PATH: {', '.join(missing)}")


def fetch_repo(repo: str, branch: str, workdir: str, do_clone: bool) -> None:
    """Clone the repo, or pull the latest changes if it already exists."""
    if not do_clone:
        if not os.path.isdir(workdir):
            sys.exit(f"error: --no-clone given but '{workdir}' does not exist")
        print(f"using existing checkout at '{workdir}' (skipping clone)")
        return

    if os.path.isdir(os.path.join(workdir, ".git")):
        print(f"repo already present in '{workdir}' — pulling latest changes")
        run(["git", "-C", workdir, "fetch", "origin", branch])
        run(["git", "-C", workdir, "checkout", branch])
        run(["git", "-C", workdir, "pull", "--ff-only", "origin", branch])
    else:
        run(["git", "clone", "--branch", branch, "--depth", "1", repo, workdir])


def build_image(workdir: str, image: str) -> None:
    """Build the image with the repo root as the build context."""
    dockerfile = os.path.join("build", "Dockerfile")
    if not os.path.isfile(os.path.join(workdir, dockerfile)):
        sys.exit(f"error: '{dockerfile}' not found inside '{workdir}'")

    # docker looks for .dockerignore at the build-context root, so copy ours there.
    src_ignore = os.path.join(workdir, "build", ".dockerignore")
    dst_ignore = os.path.join(workdir, ".dockerignore")
    if os.path.isfile(src_ignore):
        shutil.copyfile(src_ignore, dst_ignore)

    run(
        ["docker", "build", "-f", dockerfile, "-t", image, "."],
        cwd=workdir,
        env={**os.environ, "DOCKER_BUILDKIT": "1"},
    )


def run_container(image: str, container: str, port: int) -> None:
    # Remove any previous container with the same name (ignore if absent).
    subprocess.run(
        ["docker", "rm", "-f", container],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    run(
        [
            "docker", "run", "-d",
            "--name", container,
            "--restart", "unless-stopped",
            "-p", f"{port}:3000",
            image,
        ]
    )
    print(
        f"\n✅ Container '{container}' is running.\n"
        f"   URL:    http://localhost:{port}/\n"
        f"   Health: http://localhost:{port}/healthz\n"
        f"   Logs:   docker logs -f {container}\n"
        f"   Stop:   docker rm -f {container}"
    )


def main() -> None:
    p = argparse.ArgumentParser(
        description="Fetch, build and run the AIAD site Docker image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--repo", default=DEFAULT_REPO, help="git URL to clone")
    p.add_argument("--branch", default=DEFAULT_BRANCH, help="branch to build")
    p.add_argument("--workdir", default=DEFAULT_WORKDIR, help="local clone directory")
    p.add_argument("--image", default=DEFAULT_IMAGE, help="image tag to build")
    p.add_argument("--container", default=DEFAULT_CONTAINER, help="container name")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help="host port")
    p.add_argument("--no-clone", action="store_true", help="use existing --workdir as-is")
    p.add_argument("--no-run", action="store_true", help="build the image but do not run it")
    args = p.parse_args()

    ensure_prerequisites()
    fetch_repo(args.repo, args.branch, args.workdir, do_clone=not args.no_clone)
    build_image(args.workdir, args.image)

    if args.no_run:
        print(f"\n✅ Image '{args.image}' built. (--no-run, container not started)")
        return

    run_container(args.image, args.container, args.port)


if __name__ == "__main__":
    main()
