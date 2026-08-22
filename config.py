from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./lisenok.db"
    cors_origins: str = "*"
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
