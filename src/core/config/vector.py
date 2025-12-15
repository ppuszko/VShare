from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    VECTOR_DB_URL: str
    VECTOR_COLLECTION_NAME: str
    DENSE_MODEL: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    SPARSE_MODEL: str = "prithivida/Splade_PP_en_v1"
    MULTI_MODEL: str = "colbert-ir/colbertv2.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

VectorConfig = Settings() # type: ignore[arg-type]


