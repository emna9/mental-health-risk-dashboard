#!/usr/bin/env bash
# Start the Mental Health Risk Dashboard (FastAPI backend + Streamlit UI)
# and expose it publicly through a Cloudflare quick tunnel.
#
# Usage:  bash deploy/start.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKEND_PORT="${BACKEND_PORT:-8123}"
UI_PORT="${UI_PORT:-8501}"
CLOUDFLARED="${CLOUDFLARED:-$ROOT/deploy/cloudflared}"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Creating Python 3.12 venv..."
  uv venv --python 3.12 .venv
  uv pip install --python .venv/bin/python -r requirements.txt
fi

echo "Starting FastAPI backend on 127.0.0.1:$BACKEND_PORT ..."
.venv/bin/python -m uvicorn app.backend.main:app \
  --host 127.0.0.1 --port "$BACKEND_PORT" > logs_backend.log 2>&1 &

echo "Starting Streamlit on 127.0.0.1:$UI_PORT ..."
BACKEND_URL="http://127.0.0.1:$BACKEND_PORT" \
  .venv/bin/python -m streamlit run streamlit_app.py \
  --server.port "$UI_PORT" --server.address 127.0.0.1 \
  --server.headless true --browser.gatherUsageStats false \
  > logs_streamlit.log 2>&1 &

for _ in $(seq 1 40); do
  if curl -fsS -m 3 "http://127.0.0.1:$UI_PORT/" >/dev/null 2>&1; then break; fi
  sleep 2
done

if [[ -x "$CLOUDFLARED" ]]; then
  echo "Opening public tunnel ..."
  "$CLOUDFLARED" tunnel --url "http://127.0.0.1:$UI_PORT" \
    --no-autoupdate --logfile "$ROOT/tunnel.log" >/dev/null 2>&1 &
  for _ in $(seq 1 30); do
    URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$ROOT/tunnel.log" 2>/dev/null | head -1)"
    [[ -n "${URL:-}" ]] && break
    sleep 2
  done
  echo
  echo "PUBLIC URL: ${URL:-<tunnel still starting, see tunnel.log>}"
fi

echo "Local:    http://127.0.0.1:$UI_PORT"
echo "API docs: http://127.0.0.1:$BACKEND_PORT/docs"
