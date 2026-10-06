from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "change-this-development-secret"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    database_path: str = "data/pocketsmart.db"
    upload_dir: str = "uploads"
    max_upload_mb: int = 5
    access_token_expire_minutes: int = 1440
    cookie_secure: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_file(self) -> Path:
        return Path(self.database_path)

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.database_file.parent.mkdir(parents=True, exist_ok=True)
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    return settings
