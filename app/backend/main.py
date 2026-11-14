import logging
import os
import threading
import time
import urllib.request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes import analytics, health, models, predict, records

logger = logging.getLogger(__name__)

_default_origins = "http://localhost:8501,http://127.0.0.1:8501"
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]


def _keep_warm_loop(public_url: str, interval_seconds: int) -> None:
    health_url = f"{public_url.rstrip('/')}/api/v1/health"
    while True:
        time.sleep(interval_seconds)
        try:
            with urllib.request.urlopen(health_url, timeout=30):
                pass
        except Exception:
            # The next tick retries; a failed self-ping must never crash the API.
            pass


def _start_keep_warm() -> None:
    """Ping our own public URL so free hosting does not spin the API down.

    Render spins a free service down after 15 minutes without inbound traffic.
    Enable with KEEP_WARM=1; RENDER_EXTERNAL_URL is injected by Render.
    """
    enabled = os.environ.get("KEEP_WARM", "").strip().lower() in {"1", "true", "yes", "on"}
    public_url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    if not enabled or not public_url:
        return
    interval = max(300, int(os.environ.get("KEEP_WARM_INTERVAL", "600")))
    threading.Thread(
        target=_keep_warm_loop,
        args=(public_url, interval),
        name="keep-warm",
        daemon=True,
    ).start()
    logger.info("Keep-warm enabled: pinging %s every %ss", public_url, interval)


_start_keep_warm()

app = FastAPI(
    title="Mental Health Analytics API",
    description=(
        "Read-only analytics and single-record educational risk-insight API. "
        "No medical advice, diagnosis, or treatment recommendations are provided."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(health.router, prefix=PREFIX, tags=["health"])
app.include_router(records.router, prefix=PREFIX, tags=["records"])
app.include_router(analytics.router, prefix=f"{PREFIX}/analytics", tags=["analytics"])
app.include_router(models.router, prefix=f"{PREFIX}/models", tags=["models"])
app.include_router(predict.router, prefix=PREFIX, tags=["predict"])
