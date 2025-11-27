from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete
from src.db.models import User
from .schemas import UserCreate, UserLogin
from .utils import generate_hash, verify_hash
from src.errors.decorators import handle_exceptions
from src.errors.exceptions import ForbiddenError 

class UserService:
    async def get_user_by_email(self, user_email: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.email == user_email))
        return user.first()
    
    async def get_user_by_uid(self, user_uid: str, session: AsyncSession) -> User | None:
        user = await session.exec(select(User).where(User.uid == user_uid))
        return user.first()
    
    async def user_exist(self, user_email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(user_email, session)
        return user != None
    
    @handle_exceptions
    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> User | None:
        user_data_dict = user_data.model_dump()
        if not await self.user_exist(user_data_dict['email'], session):
            user = User(**user_data_dict)   
            passwd_hash = generate_hash(user_data_dict['password'])
            user.password_hash = passwd_hash

            session.add(user)
            await session.commit()
            return user
        raise ForbiddenError(detail="An account with this email already exists.")

    @handle_exceptions
    async def confirm_credentials(self, user_data: UserLogin, session: AsyncSession) -> User | None:
        user = await self.get_user_by_email(user_data.email, session)
        if user is not None:
            if verify_hash(user_data.password, user.password_hash):
                return user
        raise ForbiddenError(detail="E-mail and/or password incorrect.")
    
    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k ,v)
        
        await session.commit()
        return user
    
    


