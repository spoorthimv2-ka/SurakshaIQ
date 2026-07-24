import os
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.router import api_router
from app.core.logger import setup_logging
from app.core.exceptions import DataValidationError, RepositoryError
from zcatalyst_sdk.exceptions import CatalystError

setup_logging()

catalyst_auth_raw = os.getenv("CATALYST_AUTH")
if catalyst_auth_raw is None:
    print("CATALYST_AUTH env var: NOT SET")
else:
    truncated = catalyst_auth_raw[:30] + "...(truncated)"
    print(f"CATALYST_AUTH env var: {truncated}")
    try:
        parsed = json.loads(catalyst_auth_raw)
        keys = list(parsed.keys())
        print(f"CATALYST_AUTH JSON parse: SUCCESS, keys={keys}")
    except Exception as e:
        print(f"CATALYST_AUTH JSON parse: FAILED - {e}")

print(
    f"STARTUP CONFIG: dev_skip_auth={settings.dev_skip_auth}, "
    f"environment={settings.environment}, debug={settings.debug}"
)

app = FastAPI(
    title=settings.app_name,
    description="Zoho Catalyst AppSail Backend for SurakshaIQ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.environment == "development",
)

@app.middleware("http")
async def request_logger(request: Request, call_next):
    print(f"REQUEST: {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"RESPONSE: {response.status_code}")
    return response


cors_origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    db_label = "Mock Data Store" if settings.mock_catalyst_data else "Catalyst Data Store"
    auth_label = "Dev Bypass" if settings.dev_skip_auth else "JWT"
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": db_label,
        "authentication": auth_label,
    }
@app.get("/cors-test")
async def cors_test():
    return {
        "settings": settings.cors_origins,
    }