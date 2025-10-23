from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "local"
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    SCHEDULER_INTERVAL_MINUTES: int = 10
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    LOG_LEVEL: str | None = None
    # POLICY_DATE_MODE: str = "date_only"  
    REDIS_LOCK_KEY: str = "policy-expiry-lock"
    REDIS_LOCK_TTL_SECONDS: int = 60

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
