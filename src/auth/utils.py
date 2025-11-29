from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from src.config import Config
import uuid
import logging
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType, NameEmail
from pydantic import SecretStr
from fastapi import BackgroundTasks
from fastapi.requests import Request
from itsdangerous import URLSafeTimedSerializer
from errors.decorators import handle_exceptions
from typing import Any 

hash_context = CryptContext(
    schemes=['bcrypt']
)
ACCESS_TOKEN_EXPIRY = 3600

def generate_hash(secret: str) -> str:
    return hash_context.hash(secret)

def verify_hash(secret: str, secret_hash: str) -> bool:
    return hash_context.verify(secret, secret_hash)

def create_jwt(user_data: dict, expiry: timedelta | None = None, access: bool = True) -> str:
    payload = {}

    payload['user'] = user_data
    payload['exp'] = int((datetime.now(timezone.utc) + (expiry or timedelta(seconds=ACCESS_TOKEN_EXPIRY))).timestamp())
    payload['jti'] = str(uuid.uuid4())
    payload['access'] = access

    token = jwt.encode(
        payload=payload, 
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str | None) -> dict | None:
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
 

@handle_exceptions
def create_url_safe_token(data: dict, serializer: URLSafeTimedSerializer) -> str:
    token = serializer.dumps(data)
    return token

@handle_exceptions
def decode_url_safe_token(token: str, serializer: URLSafeTimedSerializer, max_age: int = 20) -> Any:
    token_data = serializer.loads(token, max_age=max_age)
    return token_data


async def send_mail_background(subject: str, recipients: list[NameEmail], body: str, request: Request, background_tasks: BackgroundTasks):
    message = MessageSchema(subject=subject, 
                            recipients=recipients,
                            body=body,
                            subtype=MessageType.html)
    
    background_tasks.add_task(request.app.state.fastmail.send_message, message)

def generate_confirmation_template(username: str, link: str) -> str:
    return f"""
    <h1>Verify your email</h1>
    <p>Hi {username}! 
    </br> Please click this <a href="{link}">link</a> to verify your email.
    This activation link will expire in 20 minutes.</p>
    """