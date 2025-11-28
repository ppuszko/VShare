from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .schemas import UserCreate, UserLogin, UserGet
from .dependencies import RoleChecker, APIKeyCookie

user_router = APIRouter()
user_service = UserService()

@user_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user_data.group_uid = "6ee418f7-d8b7-4678-883b-eaa8c262200e" # temp
    user = await user_service.create_user(user_data, session)
    if user is not None:
        return JSONResponse(
            content = f"Congratulations {user_data.username}, your account has been succesfully created! \
                        To activate account follow instructions sent to your e-mail address",
        )
    

@user_router.get("/", status_code=status.HTTP_200_OK, response_model=UserGet)
async def get_user(user_uid: str = "22b0bef9-bf64-4ac8-91cd-df7a3445c7bb", session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_uid(user_uid, session)
    if user is not None:
        return user