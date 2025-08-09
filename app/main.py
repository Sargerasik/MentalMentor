from fastapi import FastAPI
from app.core.settings import settings
from app.api.v1 import health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    return app

app = create_app()
