from sqlmodel import select, delete
from sqlalchemy.orm import selectinload
from fastapi import Response
from datetime import timedelta

from src.core.db.unit_of_work import UnitOfWork
from src.core.db.models import User
from src.core.config import Config
from src.auth.utils import create_jwt, decode_jwt
from .schemas import UserCreate, UserLogin
from src.auth.utils import generate_hash, verify_hash
from src.errors.decorators import handle_exceptions
from src.errors.exceptions import ForbiddenError, NotFoundError


class UserService:
    def __init__(self, uow: UnitOfWork):
        self._session = uow.get_session  

    async def get_user_by_uid(self, user_uid: str) -> User | None:
        user = await self._session.exec(
            select(User).
            options(selectinload(User.group)). # type: ignore[arg-type]
            where(User.uid == user_uid))  
        return user.first()

    async def get_user_by_email(self, user_email: str) -> User | None:
        user = await self._session.exec(
            select(User).
            where(User.email == user_email))
        return user.one_or_none()
    
    async def user_exist(self, user_email: str) -> bool:
        user = await self.get_user_by_email(user_email)
        return user != None
    
    @handle_exceptions
    async def create_user(self, user_data: UserCreate) -> User | None:
        user_data_dict = user_data.model_dump()
        if (await self.user_exist(user_data_dict['email'])) == False:
            user_data_dict["password_hash"] = generate_hash(user_data_dict.pop("password"))
            user = User(**user_data_dict)   

            self._session.add(user)
            return user
        raise ForbiddenError(detail="An account with this email already exists.")

    @handle_exceptions
    async def confirm_credentials(self, user_data: UserLogin) -> bool | None:
        user = await self.get_user_by_email(user_data.email)
        if user is not None:
            if verify_hash(user_data.password, user.password_hash):
                return True
        raise ForbiddenError(detail="E-mail and/or password incorrect.")
    
    @handle_exceptions
    async def update_user(self, user: User, user_data: dict) -> User | None:
        if await self.user_exist(user.email):
            for k, v in user_data.items():
                setattr(user, k ,v)
            return user
        raise NotFoundError("This user doesn't exist")
    
    @handle_exceptions
    async def generate_auth_tokens(self, user: User, response: Response) -> tuple[str, str]:
        token_user_dict = {"uid":str(user.uid),
                           "email":user.email, 
                           "role": user.role, 
                           "group_uid":str(user.group_uid)}

        access_token = create_jwt(token_user_dict, timedelta(minutes=Config.ACCESS_TOKEN_EXPIRATION_MINUTES), True)
        refresh_token = create_jwt(token_user_dict, timedelta(minutes=Config.REFRESH_TOKEN_EXPIRATION_MINUTES), False)

        user.refresh_jwt_hash = generate_hash(refresh_token)
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token, 
            httponly=True, 
            secure=True, 
            samesite="strict")
        
        return (access_token, refresh_token)


