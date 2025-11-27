from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    DENSE_MODEL: str
    SPARSE_MODEL: str
    MULTI_MODEL: str 
    PICTURE_STORAGE: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    APP_ENV: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()

