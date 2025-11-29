from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from .schemas import UserCreate, UserLogin, UserGet
from .dependencies import RoleChecker, APIKeyCookie
from .utils import send_mail_background, decode_url_safe_token, create_url_safe_token, generate_confirmation_template
from fastapi_mail import NameEmail
from src.config import Config
from src.errors.exceptions import BadRequest, NotFoundError


user_router = APIRouter()
user_service = UserService()

@user_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, session: AsyncSession = Depends(get_session)):
    user_data.group_uid = "6ee418f7-d8b7-4678-883b-eaa8c262200e" # temp
    user_exists = await user_service.user_exist(user_data.email, session)
    if user_exists is False:
        user = await user_service.create_user(user_data, session)
        if user is not None:
            token= create_url_safe_token({"email":user_data.email}, request.app.state.verify_email_serializer)

            recipients = [NameEmail("", user_data.email)]
            body = generate_confirmation_template(user_data.username, f"http://{Config.DOMAIN}/users/confirm-email/{token}")
            await send_mail_background("E-mail verification", recipients, body, request, background_tasks)

            return JSONResponse(
                content = "Your account has been succesfully created! \
                            To activate account follow instructions sent to your e-mail address",
            )
        
    raise BadRequest("User account with this e-mail address already exists.")

@user_router.post("/confirm-email/{token}", status_code=status.HTTP_200_OK)
async def confirm_email(token: str, request: Request, session: AsyncSession = Depends(get_session)):   
    token_data = decode_url_safe_token(token, request.app.state.verify_email_serializer)
    user = await user_service.get_user_by_email(token_data.get("email"), session)
    if user is not None:
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(content={"message": "Your account has been succesfully verified!"})
    
    raise NotFoundError("There is no account registered with tis e-mail address.")

@user_router.get("/", status_code=status.HTTP_200_OK, response_model=UserGet)
async def get_user(user_uid: str = "22b0bef9-bf64-4ac8-91cd-df7a3445c7bb", session: AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_uid(user_uid, session)
    if user is not None:
        return user