from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    app_name: str = "SurakshaIQ Backend"
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_str: str = "/api/v1"
    debug: bool = False

    # JWT / Authentication (Superseded by Catalyst Auth, kept for backward compatibility)
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Databases
    postgres_url: Optional[str] = None
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    redis_url: Optional[str] = None

    # Zoho Catalyst
    catalyst_project_id: Optional[str] = None
    catalyst_environment: str = "Development"
    catalyst_app_key: Optional[str] = None
    catalyst_app_secret: Optional[str] = None
    catalyst_base_url: Optional[str] = None

    # Zoho Catalyst Authentication
    catalyst_auth_url: Optional[str] = None
    catalyst_client_id: Optional[str] = None
    catalyst_client_secret: Optional[str] = None
    catalyst_redirect_uri: Optional[str] = None

    # Security
    cors_origins: list[str] =  [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://surakshaiq-tsocrrhj.onslate.in",
]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
