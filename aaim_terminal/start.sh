#!/usr/bin/env bash
set -euo pipefail

# Render Root Directory is set to aaim_terminal/, but the Python package
# must be imported from the repo root (parent directory).
cd "$(dirname "$0")/.."

exec uvicorn aaim_terminal.main:app --host 0.0.0.0 --port "${PORT:-8000}"
