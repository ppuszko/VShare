from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

AppConfig = Settings() # type: ignore[arg-type]


