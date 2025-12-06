from fastapi import APIRouter, status, Depends, BackgroundTasks, Response, Security
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from .schemas import UserCreate, UserLogin, UserGet
from src.auth.dependencies import RoleChecker, RefreshCookieBearer
from src.core.mail import send_mail_background, generate_confirmation_template
from src.auth.utils import decode_url_safe_token, create_url_safe_token, create_jwt, decode_jwt, verify_hash
from fastapi_mail import NameEmail
from src.core.config import Config
from src.errors.exceptions import BadRequest, NotFoundError, TokenInvalidError
from itsdangerous import SignatureExpired
from src.core.unit_of_work import UnitOfWork, get_uow

from datetime import timedelta

user_router = APIRouter()

@user_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, uow: UnitOfWork = Depends(get_uow)):
    user_data.group_uid = "6ee418f7-d8b7-4678-883b-eaa8c262200e" # temp
    async with uow:
        user_service = UserService(uow)

        user = await user_service.create_user(user_data)
        if user is not None:
            token = create_url_safe_token({"email":user_data.email}, request.app.state.verify_email_serializer)

            recipients = [NameEmail("", user_data.email)]
            body = generate_confirmation_template(user_data.username, f"http://{Config.DOMAIN}/users/confirm-email/{token}")
            await send_mail_background("E-mail verification", recipients, body, request, background_tasks)

            return JSONResponse(
                content = "Your account has been succesfully created! \
                            To activate account follow instructions sent to your e-mail address",
            )
            
    raise BadRequest("User account with this e-mail address already exists.")

@user_router.get("/confirm-email/{token}", status_code=status.HTTP_200_OK)
async def confirm_email(token: str, request: Request, response: Response, uow: UnitOfWork = Depends(get_uow)):   
    try:
        token_data = decode_url_safe_token(token, request.app.state.verify_email_serializer)
    except SignatureExpired as e:
        raise BadRequest(detail="This link has expired.") # TODO: implement new link generation

    async with uow:
        user_service = UserService(uow)

        user = await user_service.get_user_by_email(token_data.get("email"))
        if user is not None:
            await user_service.update_user(user, {"is_verified": True})

            token_user_dict = {"email":user.email, "role": user.role, "group_uid":str(user.group_uid)}
            access_token = create_jwt(token_user_dict, timedelta(minutes=Config.ACCESS_TOKEN_EXPIRATION_MINUTES), True)
            refresh_token = create_jwt(token_user_dict, timedelta(minutes=Config.REFRESH_TOKEN_EXPIRATION_MINUTES), False)
            response.set_cookie(key="refresh_token", value=refresh_token)

            return JSONResponse(content={"message": "Your account has been succesfully verified!",
                                         "access":access_token,
                                         "refresh": refresh_token})
        
    raise NotFoundError(detail="There is no account registered with this e-mail address.")


@user_router.post("/sign-in")
async def sign_in(user_data: UserLogin, response: Response, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(user_data.email)
        if user is not None:
            password_match = verify_hash(user_data.password, user.password_hash)
            if password_match:
                access_token, refresh_token = await user_service.generate_auth_tokens(user, response)

                return JSONResponse(content={"message": "Your account has been succesfully verified!",
                                            "access":access_token,
                                            "refresh": refresh_token})
        else:
            return JSONResponse(content={"message": "Incorrect e-mail or password!"})


@user_router.get("/{user_uid}", status_code=status.HTTP_200_OK, response_model=UserGet)
async def get_user(user_uid: str, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        user_service = UserService(uow)

        user = await user_service.get_user_by_uid(user_uid)
        if user is not None:
            return user
        

@user_router.post("/refresh")
async def refresh_tokens(response: Response, refresh_jwt: dict = Security(RefreshCookieBearer()), uow: UnitOfWork = Depends(get_uow)):
    token = refresh_jwt['token']
    data = refresh_jwt['data']

    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(data['user']['email'])
        if user and verify_hash(token, user.refresh_jwt_hash):
            access, _ = await user_service.generate_auth_tokens(user, response)

            return access
        raise TokenInvalidError