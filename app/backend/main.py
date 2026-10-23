from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes import analytics, health, models, predict, records

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
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(health.router, prefix=PREFIX, tags=["health"])
app.include_router(records.router, prefix=PREFIX, tags=["records"])
app.include_router(analytics.router, prefix=f"{PREFIX}/analytics", tags=["analytics"])
app.include_router(models.router, prefix=f"{PREFIX}/models", tags=["models"])
app.include_router(predict.router, prefix=PREFIX, tags=["predict"])
