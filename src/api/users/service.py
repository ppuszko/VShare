from sqlmodel import select, delete
from sqlalchemy.orm import selectinload
from fastapi import Response
from datetime import timedelta

from src.core.db.unit_of_work import UnitOfWork
from src.core.db.models import User, Document
from src.api.users.schemas import UserCreate, UserLogin, UserGet
from src.api.vectors.schemas import DocumentAdd

from src.core.config.auth import AuthConfig
from src.core.config.app import AppConfig
from src.auth.utils import create_jwt
from src.auth.utils import generate_hash, verify_hash

from src.errors.exceptions import ForbiddenError, NotFoundError


class UserService:
    def __init__(self, uow: UnitOfWork):
        self._session = uow.session  

    async def get_user_by_uid(self, user_uid: str) -> User:
        user = await self._session.exec(
            select(User).
            options(selectinload(User.group)). # type: ignore[arg-type]
            where(User.uid == user_uid))  
        
        result = user.one_or_none()
        
        if result is None:
            raise NotFoundError
        
        return result

    async def get_user_by_email(self, user_email: str) -> User:
        user = await self._session.exec(
            select(User).
            where(User.email == user_email))
        result = user.one_or_none()
        
        if result is None:
            raise NotFoundError

        return result
        
    
    async def user_exist(self, user_email: str) -> bool:
        user = await self._session.exec(
            select(User).
            where(User.email == user_email))
        return user.one_or_none() != None
    

    async def create_user(self, user_data: UserCreate) -> User:
        user_data_dict = user_data.model_dump()
        if (await self.user_exist(user_data_dict['email'])) == False:
            user_data_dict["password_hash"] = generate_hash(user_data_dict.pop("password"))
            user = User(**user_data_dict)   

            self._session.add(user)
            return user
        raise ForbiddenError(detail="An account with this email already exists.")


    async def confirm_credentials(self, user_data: UserLogin) -> bool:
        user = await self.get_user_by_email(user_data.email)
        if user is not None:
            if verify_hash(user_data.password, user.password_hash):
                return True
        raise ForbiddenError(detail="E-mail and/or password incorrect.")


    async def update_user(self, user: User, user_data: dict) -> User:
        if await self.user_exist(user.email):
            for k, v in user_data.items():
                setattr(user, k ,v)
            return user
        raise NotFoundError("This user doesn't exist")
    

    async def generate_auth_tokens(self, user: User, response: Response) -> str:
        token_user_dict = {
            "uid":str(user.uid),
            "email":user.email, 
            "role": user.role, 
            "group_uid":str(user.group_uid)}

        access_token = create_jwt(token_user_dict, timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRATION_MINUTES), True)
        refresh_token = create_jwt(token_user_dict, timedelta(minutes=AuthConfig.REFRESH_TOKEN_EXPIRATION_MINUTES), False)

        user.refresh_jwt_hash = generate_hash(refresh_token)
        response.set_cookie(
            key="refresh_token", 
            value=refresh_token, 
            httponly=True, 
            secure=AppConfig.APP_ENV != "DEV",  
            samesite="lax")
        
        return access_token
    

    async def add_documents(self, documents: list[str | None], documents_metadata: list[DocumentAdd], user: UserGet) -> list[DocumentAdd]:
        saved_docs = []
        doc_count = 0

        for file, meta in zip(documents, documents_metadata):
            if file is not None:
                doc_count += 1


                meta.group_uid = user.group.uid
                meta.user_uid = user.uid
                meta.storage_path = file

                db_doc = Document(**(meta.model_dump()))
                self._session.add(db_doc)

                saved_docs.append(db_doc)
            else:
                saved_docs.append(meta)

        if doc_count != 0:
            await self._session.flush()

            curr_user = await self.get_user_by_email(user.email)
            if curr_user:
                await self.update_user(curr_user, {"doc_count": user.doc_count + doc_count})
            
        return [DocumentAdd(**(doc.model_dump())) for doc in saved_docs]

    

