from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "FCGAA Stats"
    app_env: str = "local"
    secret_key: str = "change-me-local-secret"
    access_token_expire_minutes: int = 60

    database_url: str = Field(
        default="postgresql+psycopg://fcgaa:fcgaa_local_password@localhost:5432/fcgaa_stats"
    )

    storage_root: str = "storage"
    max_upload_mb: int = 100

    mistral_api_key: str | None = None
    mistral_model: str = "mistral-large-latest"
    ai_external_research_enabled: bool = False

    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

