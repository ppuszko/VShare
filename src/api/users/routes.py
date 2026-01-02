from fastapi import APIRouter, status, Depends, BackgroundTasks, Response, Security
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from itsdangerous import SignatureExpired

from .service import UserService
from .schemas import UserLogin, UserGet, UserInvite, UserCreate, UserMissingCredentials
from src.auth.dependencies import RoleChecker, RefreshCookieBearer
from src.auth.utils import verify_hash
from src.errors.exceptions import BadRequest, NotFoundError, TokenInvalidError
from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.core.utils.url_tokenizer import URLTokenizer, TokenType
from src.core.utils.mail_manager import MailManager, EmailType, get_mail_man
from src.errors.exceptions import TokenInvalidError

templates = Jinja2Templates(directory="src/templates")

user_router = APIRouter()

@user_router.get("/invite-user", status_code=status.HTTP_201_CREATED)
async def invite_users(users_to_invite: list[UserInvite], 
                      background_tasks: BackgroundTasks, 
                      curr_user: UserGet = Security(RoleChecker(["ADMIN"])),
                      uow: UnitOfWork = Depends(get_uow),
                      mail_man: MailManager = Depends(get_mail_man)):
    
    tokenizer = URLTokenizer(TokenType.INVITATION)
    
    async with uow:
        user_service = UserService(uow)
        for user in users_to_invite:
            if not user_service.user_exist(user.email):
                user.group_uid = str(curr_user.group.uid)

                link = tokenizer.get_tokenized_link(user.model_dump())
                recipients = [user.email]
                context = {"link": link,
                           "group_name": curr_user.group.name}
                
                await mail_man.send_templated_email(context, recipients, EmailType.INVITE, background_tasks)


@user_router.get("/validate-invite/{token}", status_code=status.HTTP_200_OK)
async def validate_invite(token: str):
    try:
        tokenizer = URLTokenizer(TokenType.INVITATION)
        token_data = tokenizer.decode_url_safe_token(token)
        return {"email": token_data["email"],
                "group_name": token_data["group_name"],
                "role": token_data["role"]}
    except SignatureExpired:
        raise TokenInvalidError


@user_router.get("/redeem-invite/{token}", status_code=status.HTTP_200_OK)
async def redeem_invite(token: str, missingCreds: UserMissingCredentials, uow: UnitOfWork = Depends(get_uow)):
    try:
        tokenizer = URLTokenizer(TokenType.INVITATION)
        token_data = tokenizer.decode_url_safe_token(token)    

        user_data = UserCreate(**(missingCreds.model_dump()), **(token_data))

        async with uow:
            user_service = UserService(uow)
            user = user_service.create_user(user_data)

    except Exception:
        raise TokenInvalidError


@user_router.get("/confirm-email/{token}", status_code=status.HTTP_200_OK)
async def confirm_email(token: str, request: Request, response: Response, uow: UnitOfWork = Depends(get_uow)):   
    try:
        tokenizer = URLTokenizer(TokenType.CONFIRMATION)
        token_data = tokenizer.decode_url_safe_token(token)

        async with uow:
            user_service = UserService(uow)

            user = await user_service.get_user_by_email(token_data.get("email"))
            if user is not None and not user.is_verified:
                await user_service.update_user(user, {"is_verified": True})
                access = await user_service.generate_auth_tokens(user, response)

                return templates.TemplateResponse(
                    "verified.html",
                    {
                        "request":request,
                        "message": "Your account has been succesfully verified"
                    }
                )
    except SignatureExpired:
        return templates.TemplateResponse(
            "verify_failed.html",
            {"request":request, 
             "message":"Activation link expired."}, # TODO: implement new link request
            status_code=404
        )
    except Exception:
        return templates.TemplateResponse(
            "verify_failed.html",
            {"request":request, 
             "message":"Confirmation link is invalid."},
            status_code=404
        )


@user_router.post("/sign-in")
async def sign_in(user_data: UserLogin, response: Response, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(user_data.email)
        if user is not None:
            password_match = verify_hash(user_data.password, user.password_hash)
            if password_match:
                access_token, refresh_token = await user_service.generate_auth_tokens(user, response)

                return access_token
        else:
            return JSONResponse(content={"message": "Incorrect e-mail or password!"})


@user_router.get("/{user_uid}", status_code=status.HTTP_200_OK, response_model=UserGet)
async def get_user(user_uid: str, uow: UnitOfWork = Depends(get_uow), curr_user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    async with uow:
        user_service = UserService(uow)

        user = await user_service.get_user_by_uid(user_uid)
        if user is not None:
            if user.group_uid == curr_user.group.uid:
                return user
        
        raise NotFoundError("There is no such user in your group!")
        

@user_router.post("/refresh")
async def refresh_tokens(response: Response, refresh_jwt: dict = Security(RefreshCookieBearer()), uow: UnitOfWork = Depends(get_uow)):
    token = refresh_jwt['token']
    data = refresh_jwt['data']

    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(data['user']['email'])
        if user and verify_hash(token, user.refresh_jwt_hash):
            access, refresh = await user_service.generate_auth_tokens(user, response)
            return access, refresh
        raise TokenInvalidError