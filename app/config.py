from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_URL: str

    REDIS_HOST: str
    REDIS_PORT: int

    API_HOST: str
    API_PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()  # type: ignore
