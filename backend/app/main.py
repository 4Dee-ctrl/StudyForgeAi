from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .exceptions import StudyForgeError
from .routers import export, extract, generate


_log_record_factory = logging.getLogRecordFactory()


def _record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
    record = _log_record_factory(*args, **kwargs)
    if not hasattr(record, "request_id"):
        record.request_id = "-"
    return record


logger = logging.getLogger("studyforge")
if not logger.handlers:
    logging.setLogRecordFactory(_record_factory)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(request_id)s] %(message)s",
    )


app = FastAPI(
    title="StudyForge API",
    description="AI-powered study aid generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


_WINDOW_SECONDS = 60
_rate_state: dict[str, tuple[float, int]] = {}


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _is_rate_limited(ip: str, now: float) -> bool:
    window_start, count = _rate_state.get(ip, (now, 0))
    if now - window_start >= _WINDOW_SECONDS:
        window_start, count = now, 0

    if count >= settings.rate_limit_per_minute:
        _rate_state[ip] = (window_start, count)
        return True

    _rate_state[ip] = (window_start, count + 1)
    return False


def _error_payload(error: str, detail: str, status_code: int) -> dict[str, Any]:
    return {"error": error, "detail": detail, "status_code": status_code}


@app.middleware("http")
async def request_id_logging_and_rate_limit(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    started = time.perf_counter()

    if request.url.path != "/api/health" and request.method != "OPTIONS":
        ip = _get_client_ip(request)
        if _is_rate_limited(ip=ip, now=time.time()):
            duration_ms = (time.perf_counter() - started) * 1000
            logger.warning(
                f"{request.method} {request.url.path} -> 429 ({duration_ms:.1f}ms)",
                extra={"request_id": request_id},
            )
            resp = JSONResponse(
                status_code=429,
                content=_error_payload(
                    error="RateLimitError",
                    detail="Rate limit exceeded. Please try again shortly.",
                    status_code=429,
                ),
            )
            resp.headers["X-Request-ID"] = request_id
            return resp

    response = await call_next(request)
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)",
        extra={"request_id": request_id},
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(StudyForgeError)
async def handle_studyforge_error(request: Request, exc: StudyForgeError):
    request_id = getattr(request.state, "request_id", "-")
    resp = JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.error, exc.detail, exc.status_code),
    )
    resp.headers["X-Request-ID"] = request_id
    return resp


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "-")
    resp = JSONResponse(
        status_code=422,
        content=_error_payload(
            error="ValidationError",
            detail=str(exc),
            status_code=422,
        ),
    )
    resp.headers["X-Request-ID"] = request_id
    return resp


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", "-")
    resp = JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            error="HTTPException",
            detail=str(exc.detail),
            status_code=exc.status_code,
        ),
    )
    resp.headers["X-Request-ID"] = request_id
    return resp


@app.exception_handler(Exception)
async def handle_unhandled_exception(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__}",
        extra={"request_id": request_id},
    )
    resp = JSONResponse(
        status_code=500,
        content=_error_payload(
            error="InternalServerError",
            detail="An unexpected error occurred. Please try again.",
            status_code=500,
        ),
    )
    resp.headers["X-Request-ID"] = request_id
    return resp


@app.get(
    "/api/health",
    tags=["Health"],
    summary="Health check",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(extract.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(export.router, prefix="/api")
