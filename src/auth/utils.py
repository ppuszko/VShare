from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from src.core.config import Config
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer
from src.errors.decorators import handle_exceptions
from typing import Any 

hash_context = CryptContext(
    schemes=['bcrypt']
)
ACCESS_TOKEN_EXPIRY = 3600

def generate_hash(secret: str) -> str:
    return hash_context.hash(secret)

def verify_hash(secret: str, secret_hash: str) -> bool:
    return hash_context.verify(secret, secret_hash)

def create_jwt(user_data: dict, expiry: timedelta, access: bool) -> str:
    payload = {}

    payload['user'] = user_data
    payload['exp'] = int((datetime.now(timezone.utc) + (expiry)).timestamp())
    payload['jti'] = str(uuid.uuid4())
    payload['access'] = access

    token = jwt.encode(
        payload=payload, 
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_jwt(token: str | None) -> dict | None:
    if token is not None:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=Config.JWT_SECRET,
                algorithms=Config.JWT_ALGORITHM
            )
            return token_data
        except jwt.PyJWTError as e:
            logging.exception(f"Failed to decode token. Message: {e}\n")
    return None


def create_url_safe_token(data: dict, serializer: URLSafeTimedSerializer) -> str:
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str, serializer: URLSafeTimedSerializer, max_age: int = 1200) -> Any:
    token_data = serializer.loads(token, max_age=max_age)
    return token_data


