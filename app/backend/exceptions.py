from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )
