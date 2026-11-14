#!/usr/bin/env bash
# Container entrypoint with three modes:
#   APP_MODE=full  API on loopback + dashboard on $PORT (single-container hosts, compose)
#   APP_MODE=api   API only on 0.0.0.0:$PORT (dedicated service)
#   APP_MODE=ui    dashboard only on 0.0.0.0:$PORT, proxies to BACKEND_URL
set -euo pipefail

MODE="${APP_MODE:-full}"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
PORT="${PORT:-8501}"

run_api() {
  python -m uvicorn app.backend.main:app \
    --host "$1" \
    --port "$2" \
    --proxy-headers \
    "--forwarded-allow-ips=*"
}

run_ui() {
  python -m streamlit run streamlit_app.py \
    --server.port "${PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.fileWatcherType none \
    --browser.gatherUsageStats false
}

case "${MODE}" in
  api)
    echo "[entrypoint] API-only mode on 0.0.0.0:${PORT}"
    exec python -m uvicorn app.backend.main:app \
      --host 0.0.0.0 \
      --port "${PORT}" \
      --proxy-headers \
      "--forwarded-allow-ips=*"
    ;;
  ui)
    if [[ -z "${BACKEND_URL:-}" ]]; then
      echo "[entrypoint] BACKEND_URL is required when APP_MODE=ui" >&2
      exit 1
    fi
    echo "[entrypoint] dashboard-only mode on 0.0.0.0:${PORT} -> ${BACKEND_URL}"
    exec python -m streamlit run streamlit_app.py \
      --server.port "${PORT}" \
      --server.address 0.0.0.0 \
      --server.headless true \
      --server.fileWatcherType none \
      --browser.gatherUsageStats false
    ;;
  full)
    echo "[entrypoint] starting API on ${BACKEND_HOST}:${BACKEND_PORT}"
    run_api "${BACKEND_HOST}" "${BACKEND_PORT}" &
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

    echo "[entrypoint] starting dashboard on 0.0.0.0:${PORT}"
    export BACKEND_URL="${BACKEND_URL:-http://${BACKEND_HOST}:${BACKEND_PORT}}"
    run_ui &
    UI_PID=$!
    wait "${UI_PID}"
    ;;
  *)
    echo "[entrypoint] unknown APP_MODE: ${MODE} (expected full, api or ui)" >&2
    exit 1
    ;;
esac
