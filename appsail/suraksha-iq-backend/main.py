from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="Zoho Catalyst AppSail Backend for SurakshaIQ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.environment == "development",
)

cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()] if settings.cors_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.api_v1_str)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "Catalyst Data Store",
        "authentication": "JWT",
    }
