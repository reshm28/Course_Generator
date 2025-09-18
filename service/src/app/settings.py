from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DDD FastAPI Service"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
