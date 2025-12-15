from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    DB_URL: str
    REDIS_URL: str
    PICTURE_STORAGE_PATH: str
    DEFAULT_PICTURE_PATH: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

DBConfig = DBSettings() # type: ignore[arg-type]
 