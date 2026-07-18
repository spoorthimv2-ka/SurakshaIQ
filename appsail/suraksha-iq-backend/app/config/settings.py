from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    app_name: str = "SurakshaIQ Backend"
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_str: str = "/api/v1"
    
    # JWT / Authentication
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day default

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
