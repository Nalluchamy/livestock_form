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

    # Security & Authentication
    SECRET_KEY: str = "replace_me_in_production_secret_key_jwt_512"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    LOCKOUT_MAX_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    SECURE_COOKIES: bool = False

    # Default Bootstrapped Admin
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: str = "AdminSecurePass2026!"
    ADMIN_DEFAULT_EMAIL: str = "admin@elhgs.internal"

    # Uploads & Storage
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15MB

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
