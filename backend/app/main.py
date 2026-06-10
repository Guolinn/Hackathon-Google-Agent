from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_agent,
    routes_approvals,
    routes_briefings,
    routes_dashboard,
    routes_datasources,
    routes_dispatch,
    routes_health,
    routes_resources,
    routes_suppliers,
)
from app.config import get_settings
from app.api.response import envelope


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="CrisisFlow AI Backend",
        version="0.1.0",
        description="Emergency medical supply coordination backend for the CrisisFlow hackathon demo.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes_health.router)
    app.include_router(routes_dashboard.router, prefix="/api")
    app.include_router(routes_datasources.router, prefix="/api")
    app.include_router(routes_agent.router, prefix="/api")
    app.include_router(routes_resources.router, prefix="/api")
    app.include_router(routes_suppliers.router, prefix="/api")
    app.include_router(routes_dispatch.router, prefix="/api")
    app.include_router(routes_approvals.router, prefix="/api")
    app.include_router(routes_briefings.router, prefix="/api")

    @app.get("/")
    def root() -> dict:
        return envelope(
            {
                "service": "crisisflow-backend",
                "status": "ok",
                "docs": "/docs",
                "health": "/health",
                "api_base": "/api",
            },
            data_mode_used=settings.data_mode,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope(None, success=False, error=str(exc.detail), data_mode_used="mock"),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=envelope(None, success=False, error=str(exc), data_mode_used="mock"),
        )
    return app


app = create_app()
