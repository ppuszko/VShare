from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 1
    REFRESH_TOKEN_EXPIRATION_MINUTES: int = 60 * 24 * 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

AuthConfig = Settings() # type: ignore[arg-type]
