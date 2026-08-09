#!/usr/bin/env bash
# Runs on the server (invoked over SSH by .github/workflows/deploy.yml on
# every push to main). Pulls the new commit, rebuilds the web image and
# restarts the stack. Migrations + collectstatic happen automatically in
# docker/entrypoint.sh when the "web" container starts.
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/portfolio}"
cd "$APP_DIR"

echo "==> Fetching origin/main"
git fetch origin main
git reset --hard origin/main

mkdir -p media

echo "==> Rebuilding and restarting the stack"
docker compose up -d --build

echo "==> Pruning dangling images"
docker image prune -f

echo "==> Deploy finished: $(git rev-parse --short HEAD)"
