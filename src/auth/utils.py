import logging
import uuid
from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from src.core.config.auth import AuthConfig



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
        key=AuthConfig.JWT_SECRET,
        algorithm=AuthConfig.JWT_ALGORITHM
    )

    return token

def decode_jwt(token: str | None) -> dict | None:
    if token is not None:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=AuthConfig.JWT_SECRET,
                algorithms=AuthConfig.JWT_ALGORITHM
            )
            return token_data
        except jwt.PyJWTError as e:
            logging.exception(f"Failed to decode token. Message: {e}\n")
    return None
