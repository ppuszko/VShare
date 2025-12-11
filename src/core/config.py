from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import ConnectionConfig
from pydantic import SecretStr

class Settings(BaseSettings):
    DB_URL: str
    REDIS_URL: str
    VECTOR_DB_URL: str
    VECTOR_COLLECTION_NAME: str
    DENSE_MODEL: str
    SPARSE_MODEL: str
    MULTI_MODEL: str 
    PICTURE_STORAGE: str
    DEFAULT_PICTURE: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRATION_MINUTES: int
    APP_ENV: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    CONFIRM_MAIL_SUBJECT: str


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings() # type: ignore[arg-type]

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(Config.MAIL_PASSWORD),
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_FROM_NAME = Config.MAIL_FROM_NAME,
    MAIL_STARTTLS = Config.MAIL_STARTTLS,
    MAIL_SSL_TLS = Config.MAIL_SSL_TLS,
    USE_CREDENTIALS = Config.USE_CREDENTIALS,
    VALIDATE_CERTS = Config.VALIDATE_CERTS,
)

