"""
PolarSync Platform - FastAPI Main Application Entrypoint
SIH Problem Statement: SIH26062
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="PolarSync — Integrated Polar Expedition Logistics and Asset Management System (SIH26062)",
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware for React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root level health endpoint
@app.get("/api/health", tags=["Health"])
def get_root_health():
    """
    Standard top-level health endpoint.
    """
    return {
        "status": "ok",
        "service": "polarsync-api"
    }

# Include V1 API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root_info():
    return {
        "system": "PolarSync Platform",
        "description": "Integrated Polar Expedition Logistics and Asset Management System",
        "problem_statement": "SIH26062",
        "api_docs": "/docs",
        "health_check": "/api/v1/health"
    }
