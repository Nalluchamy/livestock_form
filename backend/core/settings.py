from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Core application settings.
    Powered by pydantic-settings, reads from environment variables or .env file.
    """

    # Project metadata
    PROJECT_NAME: str = "Explainable Livestock Health Grading System (ELHGS)"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./elhgs.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "livestock_grading"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # Security (Placeholder for future phases)
    SECRET_KEY: str = "replace_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Offline Mode / Sync
    OFFLINE_MODE_ENABLED: bool = False
    SYNC_INTERVAL_SECONDS: int = 3600

    # Hackathon Demo Mode
    DEMO_MODE: bool = True

    @property
    def database_url(self) -> str:
        """Construct the database URL from settings."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
