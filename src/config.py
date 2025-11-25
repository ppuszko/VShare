from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    SAVE_DIR: str
    EMB_MODEL: str 
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()

