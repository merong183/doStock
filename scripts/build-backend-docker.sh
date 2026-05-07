#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Building dostock-api..."
docker build -t dostock-api -f "${ROOT}/backend/Dockerfile" "${ROOT}/backend"
echo ""
echo "Run locally:"
echo '  docker run --rm -p 8000:8000 -e CORS_ORIGINS=https://YOUR_APP.vercel.app dostock-api'
