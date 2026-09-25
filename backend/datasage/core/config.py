"""Application configuration — loaded from environment variables and .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """DataSage application settings.

    All values are loaded from environment variables.
    Defaults are suitable for local development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---------------------------------------------------------
    APP_NAME: str = "DataSage"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_LOG_LEVEL: str = "DEBUG"
    APP_SECRET_KEY: str = "change-me-to-a-random-string"

    # --- Database (PostgreSQL + PostGIS) -------------------------------------
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "datasage"
    POSTGRES_USER: str = "datasage"
    POSTGRES_PASSWORD: str = "change-me"
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 20

    @property
    def DATABASE_URL(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync URL for Alembic migrations."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # --- Redis ---------------------------------------------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_CACHE_TTL_SECONDS: int = 3600

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection URL."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # --- JWT Authentication --------------------------------------------------
    JWT_SECRET_KEY: str = "change-me-to-another-random-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ----------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # --- ML Model Configuration ----------------------------------------------
    ML_MODEL_DIR: str = "./ml/models"
    ML_VALUATION_MODEL_NAME: str = "valuation_xgb_v1.joblib"
    ML_PREDICTION_CACHE_TTL: int = 86400
    ML_BATCH_SIZE: int = 100
    ML_MIN_CONFIDENCE_THRESHOLD: float = 0.6

    # --- Geospatial Configuration --------------------------------------------
    OVERPASS_API_URL: str = "https://overpass-api.de/api/interpreter"
    OVERPASS_TIMEOUT_SECONDS: int = 30
    OVERPASS_MAX_RETRIES: int = 3
    GEO_DEFAULT_SRID: int = 4326
    GEO_SEARCH_RADIUS_METERS: int = 5000
    GEO_DELHI_NCR_BBOX: str = "28.3,76.8,28.9,77.6"

    # --- Rate Limiting -------------------------------------------------------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_ML: str = "20/minute"

    # --- Feature Flags -------------------------------------------------------
    FEATURE_COMPARISON: bool = True
    FEATURE_RECOMMENDATIONS: bool = True
    FEATURE_INVESTMENT_SCORE: bool = True
    FEATURE_SOCIAL_LOGIN: bool = False
    FEATURE_MAP_SEARCH: bool = False
    FEATURE_NOTIFICATIONS: bool = False


settings = Settings()
