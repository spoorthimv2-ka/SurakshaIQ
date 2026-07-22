from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.core.logger import setup_logging
from app.core.exceptions import DataValidationError, RepositoryError
from zcatalyst_sdk.exceptions import CatalystError
import os

setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="Zoho Catalyst AppSail Backend for SurakshaIQ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.environment == "development",
)

cors_origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.api_v1_str)

@app.exception_handler(DataValidationError)
async def data_validation_exception_handler(request: Request, exc: DataValidationError):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@app.exception_handler(RepositoryError)
async def repository_exception_handler(request: Request, exc: RepositoryError):
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

@app.exception_handler(CatalystError)
async def catalyst_exception_handler(request: Request, exc: CatalystError):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Catalyst Data Store is temporarily unavailable")

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "Catalyst Data Store",
        "authentication": "JWT",
    }
