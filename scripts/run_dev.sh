#!/usr/bin/env bash
# Quick dev launcher. Usage: ./scripts/run_dev.sh [port]
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-8000}"

# Ensure .env exists
if [[ ! -f .env ]]; then
  echo "[run_dev] .env mancante. Lo creo da .env.example…"
  cp .env.example .env
  echo "[run_dev] ⚠️  Modifica .env con il tuo FIGMA_ACCESS_TOKEN reale, poi rilancia."
  exit 1
fi

# Free the port if busy
if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[run_dev] Porta ${PORT} occupata, libero il processo…"
  lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t | xargs -r kill -9 || true
  sleep 1
fi

# Pick venv python if available
PY=python
if [[ -x .venv/bin/python ]]; then PY=.venv/bin/python; fi

exec "${PY}" -m uvicorn app.main:app --reload --host 127.0.0.1 --port "${PORT}"

