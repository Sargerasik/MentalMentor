# app/core/observability.py
from __future__ import annotations
import time
import uuid
import contextvars
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

from prometheus_client import Counter, Histogram, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest

# ---- Correlation ID ----
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        req_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request_id_ctx.set(req_id)
        # прокинем в scope, чтобы логгеры/роуты могли достать
        request.scope["request_id"] = req_id

        response = await call_next(request)
        response.headers[self.header_name] = req_id
        return response

def get_request_id() -> str:
    rid = request_id_ctx.get()
    return rid or ""

# ---- Prometheus ----
REGISTRY = CollectorRegistry(auto_describe=True)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
    registry=REGISTRY,
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            elapsed = time.perf_counter() - start
            # стараемся получить шаблон маршрута, иначе фактический путь
            path = request.scope.get("route").path if request.scope.get("route") else request.url.path
            method = request.method
            REQUEST_COUNT.labels(method=method, path=path, status_code=str(status)).inc()
            REQUEST_LATENCY.labels(method=method, path=path, status_code=str(status)).observe(elapsed)
        return response

async def metrics_endpoint(_: Request) -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
