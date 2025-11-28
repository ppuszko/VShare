from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, APIKeyCookie
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from src.db.main import get_session
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from src.errors.decorators import handle_exceptions
from src.errors.exceptions import NotVerifiedError, ForbiddenError, TokenInvalidError


user_service = UserService()

class RefreshCookieBearer:
    def __init__(self, cookie_name: str = "refresh_token"):
        self.cookie_handler = APIKeyCookie(name=cookie_name)

    @handle_exceptions
    async def __call__(self, request: Request):
        refresh_cookie = await self.cookie_handler.__call__(request)
        token_data = decode_token(refresh_cookie)
        if token_data is None:
            raise TokenInvalidError
        
        self.confirm_token_type(token_data)

        return token_data

    def confirm_token_type(self, token_data: dict):
        if token_data['access']:
            raise TokenInvalidError


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    @handle_exceptions
    async def __call__(self, request: Request) -> dict | None:
        creds = await super().__call__(request)
        if creds is None:
            raise TokenInvalidError
        
        token_data = decode_token(creds.credentials)
        if token_data is None:
            raise TokenInvalidError
        
        self.verify_token_type(token_data)

        return token_data

    def verify_token_type(self, token_data) -> None:
        raise NotImplementedError("Please implement this method")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_type(self, token_data: dict):
        if not token_data['access']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This is a refresh token. Please provide an access token.")
        
        

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_email(token_details['user']['email'], session)
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

        