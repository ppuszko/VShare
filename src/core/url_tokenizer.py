from fastapi.requests import Request
from itsdangerous import URLSafeTimedSerializer

from src.core.config import Config

from typing import Any
from enum import Enum

class TokenType(Enum):
    CONFIRMATION = ("confirm-email", f"{Config.DOMAIN}/confirm-email/")
    INVITATION = ("redeem-invite", f"{Config.DOMAIN}/redeem-invite/")

    def __init__(self, salt: str, route: str):
        self.salt = salt
        self.route = route


class URLTokenizer:

    def __init__(self, token_type: TokenType, token_max_age: int = 1200):
        self.serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt=token_type.salt)
        self.route = token_type.route  
        self.max_age = token_max_age


    def get_tokenized_link(self, data: dict):
        token = self.create_url_safe_token(data)
        return self.route + token


    def create_url_safe_token(self, data: dict) -> str:
        token = self.serializer.dumps(data)
        return token


    def decode_url_safe_token(self, token: str) -> Any:
        token_data = self.serializer.loads(token, max_age=self.max_age)
        return token_data

