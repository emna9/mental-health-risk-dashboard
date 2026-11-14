# Production image: FastAPI backend + Streamlit dashboard in one container.
# The dashboard proxies to the API over loopback, so only the UI port is exposed.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BACKEND_HOST=127.0.0.1 \
    BACKEND_PORT=8000 \
    BACKEND_URL=http://127.0.0.1:8000 \
    PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1

# libgomp1 is required by scikit-learn / XGBoost wheels; curl powers the health check.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-runtime.txt ./
RUN pip install --no-cache-dir -r requirements-runtime.txt

COPY app ./app
COPY data ./data
COPY models ./models
COPY streamlit_app.py ./
COPY .streamlit ./.streamlit
COPY deploy/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD sh -c 'curl -fsS "http://127.0.0.1:${PORT}/_stcore/health" || curl -fsS "http://127.0.0.1:${PORT}/api/v1/health" || exit 1'

CMD ["/usr/local/bin/entrypoint.sh"]
