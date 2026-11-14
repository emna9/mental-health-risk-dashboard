#!/usr/bin/env bash
# Container entrypoint: start the FastAPI backend, wait until it is healthy,
# then run Streamlit in the foreground. Works on any Docker host (Render,
# Railway, Fly.io, a VPS, docker compose).
set -euo pipefail

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
UI_PORT="${PORT:-8501}"
export BACKEND_URL="${BACKEND_URL:-http://${BACKEND_HOST}:${BACKEND_PORT}}"

echo "[entrypoint] starting API on ${BACKEND_HOST}:${BACKEND_PORT}"
python -m uvicorn app.backend.main:app \
  --host "${BACKEND_HOST}" \
  --port "${BACKEND_PORT}" \
  --proxy-headers \
  --forwarded-allow-ips='*' &
API_PID=$!

UI_PID=""
shutdown() {
  [[ -n "${UI_PID}" ]] && kill -TERM "${UI_PID}" 2>/dev/null || true
  kill -TERM "${API_PID}" 2>/dev/null || true
}
trap shutdown INT TERM EXIT

for _ in $(seq 1 60); do
  if curl -fsS -m 2 "http://${BACKEND_HOST}:${BACKEND_PORT}/api/v1/health" >/dev/null 2>&1; then
    echo "[entrypoint] API is ready"
    break
  fi
  if ! kill -0 "${API_PID}" 2>/dev/null; then
    echo "[entrypoint] API exited during startup" >&2
    exit 1
  fi
  sleep 2
done

echo "[entrypoint] starting dashboard on 0.0.0.0:${UI_PORT}"
python -m streamlit run streamlit_app.py \
  --server.port "${UI_PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false &
UI_PID=$!

wait "${UI_PID}"
