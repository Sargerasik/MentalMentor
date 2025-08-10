# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.settings import settings
from app.api.v1 import health, user, auth
from app.core.observability import PrometheusMiddleware, CorrelationIdMiddleware, metrics_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(settings.redis_dsn, encoding="utf-8", decode_responses=True)
    yield
    await app.state.redis.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # middlewares: сначала correlation-id, затем метрики
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(PrometheusMiddleware)

    # routes
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(user.router, prefix="/api/v1/users", tags=["users"])

    # /metrics без аутентификации — так принято для Prometheus; если нужно — вынесем за ingress
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

    return app

app = create_app()
