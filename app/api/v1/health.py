# app/api/v1/health.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from time import perf_counter_ns
from app.services.storage import head_bucket
from app.db.session import get_session

router = APIRouter()


@router.get("/live")
async def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request, db: AsyncSession = Depends(get_session)) -> dict:
    results: dict = {"status": "ok", "components": {}}

    # --- DB check ---
    t0 = perf_counter_ns()
    try:
        # простая проверка + версия БД
        ver = await db.execute(text("select version()"))
        db_version: str = ver.scalar_one()
        db_ok = True
        err = None
    except Exception as e:
        db_ok = False
        err = str(e)
        results["status"] = "degraded"
        db_version = None
    db_ms = (perf_counter_ns() - t0) / 1_000_000

    results["components"]["postgres"] = {
        "ok": db_ok,
        "latency_ms": round(db_ms, 2),
        "version": db_version,
        "error": err,
    }

    # --- Redis check ---
    t1 = perf_counter_ns()
    try:
        pong = await request.app.state.redis.ping()
        redis_ok = bool(pong)
        err = None
    except Exception as e:
        redis_ok = False
        err = str(e)
        results["status"] = "degraded"
    redis_ms = (perf_counter_ns() - t1) / 1_000_000

    results["components"]["redis"] = {
        "ok": redis_ok,
        "latency_ms": round(redis_ms, 2),
        "error": err,
    }

    t2 = perf_counter_ns()
    try:
        ok = head_bucket()
        s3_ok, err = bool(ok), None
    except Exception as e:
        s3_ok, err = False, str(e)
        results["status"] = "degraded"
    s3_ms = (perf_counter_ns() - t2) / 1_000_000
    results["components"]["s3"] = {"ok": s3_ok, "latency_ms": round(s3_ms, 2), "bucket": settings.S3_BUCKET,
                                   "error": err}

    # Итоговый статус
    if not results["components"]["postgres"]["ok"] or not results["components"]["redis"]["ok"]:
        results["status"] = "critical" if not results["components"]["postgres"]["ok"] else results["status"]


    return results
