from fastapi import Request, Depends, Security, Response
from fastapi.security import HTTPBearer, APIKeyCookie
from datetime import datetime, timezone

from .utils import decode_jwt, verify_hash
from src.core.unit_of_work import get_uow, UnitOfWork
from src.core.db.models import User
from src.api.users.service import UserService
from src.errors.decorators import handle_exceptions
from src.errors.exceptions import NotVerifiedError, ForbiddenError, TokenInvalidError, TokenExpiredError


class RefreshCookieBearer:
    def __init__(self, cookie_name: str = "refresh_token"):
        self.cookie_handler = APIKeyCookie(name=cookie_name)

    @handle_exceptions
    async def __call__(self, request: Request, response: Response) -> dict | None:
        refresh_token = await self.cookie_handler.__call__(request)
        token_data = decode_jwt(refresh_token)

        now = datetime.now(timezone.utc).timestamp()
        if token_data is None or token_data['access'] or token_data['exp'] < now:
            raise TokenInvalidError


        return {"data":token_data, "token": refresh_token}

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    @handle_exceptions
    async def __call__(self, request: Request) -> dict | None:
        creds = await super().__call__(request)
        if creds is None:
            raise TokenInvalidError
        
        token_data = decode_jwt(creds.credentials)
        if token_data is None or not token_data['access']:
            raise TokenInvalidError
        
        now = datetime.now(timezone.utc).timestamp()
        if token_data['exp'] < now:
            raise TokenExpiredError

        return token_data

    def is_access_token_valid(self, token_data) -> bool:
        if not token_data['access']:
            raise TokenInvalidError(detail="This is a refresh token. Please provide an access token.")
        elif token_data['exp'] < datetime.now():
            return False
        else:
            return True
        
    async def request_new_access_token(self, token: dict = Security(RefreshCookieBearer())):
        if token is not None:
            return token
        

async def get_current_user(token_details: dict = Security(TokenBearer()), uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(token_details['user']['email'])
        return user


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    @handle_exceptions
    def __call__(self, current_user: User = Depends(get_current_user)) -> bool | None:
        if not current_user.is_verified:
            raise NotVerifiedError
        if current_user.role in self.allowed_roles:
            return True        
        raise ForbiddenError

        