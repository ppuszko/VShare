from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    STORAGE_PATH: str
    DEFAULT_PICTURE_PATH: str
    MIN_CONTEXT_LENGTH: int = 1500
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

FileConfig = Settings() # type: ignore[arg-type]


