from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ALLOWED_EXTENSIONS: str = "pdf,txt"
    PICTURE_STORAGE_PATH: str
    DEFAULT_PICTURE_PATH: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

FileConfig = Settings() # type: ignore[arg-type]


