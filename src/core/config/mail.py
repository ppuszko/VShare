from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import ConnectionConfig
from pydantic import SecretStr
from fastapi_mail import FastMail

class MailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_FROM: str

    MAIL_FROM_NAME: str = "VShare"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

def init_mail() -> FastMail:
    Config = MailSettings() #type: ignore

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

    return FastMail(mail_config)