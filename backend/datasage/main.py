"""FastAPI application factory.

See docs/08-backend-architecture.md for the full backend design.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from datasage.core.config import settings
from datasage.core.database import engine, init_db
from datasage.core.exceptions import DataSageError
from datasage.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    logging.basicConfig(
        level=getattr(logging, settings.APP_LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    try:
        await init_db()
        logger.info("DataSage %s started (env=%s)", settings.APP_VERSION, settings.APP_ENV)
    except Exception as e:
        logger.warning("Database connection failed on startup: %s. Continuing in offline mode.", e)

    # In development, auto-create tables and seed data
    if settings.APP_ENV == "development":
        try:
            from sqlalchemy import text

            from datasage.cli.seed import create_tables, run_seed
            from datasage.core.database import async_session_factory

            await create_tables()

            # Check if data already seeded
            async with async_session_factory() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM city"))
                count = result.scalar() or 0

            if count == 0:
                logger.info("Development mode: auto-seeding database...")
                await run_seed(count=500)
                logger.info("Auto-seeding complete.")
        except Exception as e:
            logger.warning("Auto-setup skipped: %s", e)

    yield  # Application runs here

    # Shutdown
    with suppress(Exception):
        from datasage.core.redis import close_redis
        await close_redis()
    with suppress(Exception):
        await engine.dispose()
    logger.info("DataSage shut down gracefully.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered real-estate decision-support platform",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        openapi_url="/openapi.json" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware (outermost → innermost) ──────────────────────────────────
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ─────────────────────────────────────────────────
    @app.exception_handler(DataSageError)
    async def datasage_error_handler(request: Request, exc: DataSageError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id,
                    **({} if not exc.details else {"details": exc.details}),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception("Unhandled exception", extra={"request_id": request_id})
        message = str(exc) if settings.APP_DEBUG else "An unexpected error occurred"
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": message,
                    "request_id": request_id,
                }
            },
        )

    # ── Routers ────────────────────────────────────────────────────────────
    _register_routers(app)

    # ── Health check ───────────────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health() -> dict[str, Any]:
        """Health check with DB and Redis connectivity verification."""
        from sqlalchemy import text as sa_text

        from datasage.core.database import async_session_factory
        from datasage.core.redis import is_redis_available

        checks: dict[str, str] = {"api": "ok"}

        # Database check
        try:
            async with async_session_factory() as session:
                await session.execute(sa_text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"

        # Redis check
        redis_ok = await is_redis_available()
        checks["redis"] = "ok" if redis_ok else "unavailable"

        return {
            "status": "ok",
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
            "checks": checks,
        }

    return app


def _register_routers(app: FastAPI) -> None:
    """Import and mount all API routers."""
    from datasage.api.v1.router import api_v1_router

    app.include_router(api_v1_router, prefix="/api/v1")


app = create_app()
