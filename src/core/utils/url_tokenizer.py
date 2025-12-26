from typing import Any
from enum import Enum

from fastapi.requests import Request
from itsdangerous import URLSafeTimedSerializer

from src.core.config.auth import AuthConfig
from src.core.config.app import AppConfig



class TokenType(Enum):
    CONFIRMATION = ("confirm-email", f"{AppConfig.DOMAIN}/confirm-email/")
    INVITATION = ("redeem-invite", f"{AppConfig.DOMAIN}/redeem-invite/")
    EMBEDDING_REPORT = ("embedding-report", f"{AppConfig.DOMAIN}/embedding-report/")

    def __init__(self, salt: str, route: str):
        self.salt = salt
        self.route = route


class URLTokenizer:
    def __init__(self, token_type: TokenType, token_max_age_minutes: int = 20):
        self.serializer = URLSafeTimedSerializer(AuthConfig.JWT_SECRET, salt=token_type.salt)
        self.route = token_type.route  
        self.max_age = token_max_age_minutes

    def get_tokenized_link(self, data: dict) -> str:
        token = self.create_url_safe_token(data)
        return self.route + token


    def create_url_safe_token(self, data: dict) -> str:
        return self.serializer.dumps(data)


    def decode_url_safe_token(self, token: str) -> Any:
        token_data = self.serializer.loads(token, max_age=self.max_age)
        return token_data

