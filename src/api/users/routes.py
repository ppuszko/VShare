from fastapi import APIRouter, status, Depends, BackgroundTasks, Response, Security, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from itsdangerous import SignatureExpired

from src.api.users.service import UserService
from src.api.users.schemas import UserLogin, UserGet, UserInvite, UserCreate, UserMissingCredentials

from src.auth.utils import verify_hash
from src.auth.dependencies import RoleChecker, RefreshCookieBearer

from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.core.utils.url_tokenizer import URLTokenizer, TokenType
from src.core.utils.mail_manager import MailManager, EmailType, get_mail_man




templates = Jinja2Templates(directory="src/templates")

user_router = APIRouter()

@user_router.post("/invite-user", status_code=status.HTTP_201_CREATED)
async def invite_users(users_to_invite: list[UserInvite], 
                      background_tasks: BackgroundTasks, 
                      curr_user: UserGet = Security(RoleChecker(["ADMIN"])),
                      uow: UnitOfWork = Depends(get_uow),
                      mail_man: MailManager = Depends(get_mail_man)):
    
    tokenizer = URLTokenizer(TokenType.INVITATION)
    
    async with uow:
        user_service = UserService(uow)
        for user in users_to_invite:
            if not await user_service.user_exist(user.email):
                user.group_uid = str(curr_user.group.uid)
                user.group_name = curr_user.group.name 

                link = tokenizer.get_tokenized_link(user.model_dump())
                recipients = [user.email]
                context = {"link": link,
                           "group_name": curr_user.group.name}
                
                await mail_man.send_templated_email(context, recipients, EmailType.INVITE, background_tasks)


@user_router.get("/validate-invite/{token}", status_code=status.HTTP_200_OK)
async def validate_invite(token: str):
    tokenizer = URLTokenizer(TokenType.INVITATION, 1000) # TODO: remove time limit 1000
    token_data = tokenizer.decode_url_safe_token(token)

    return JSONResponse(
        content={"email": token_data["email"],
        "group_name": token_data["group_name"],
        "role": token_data["role"]})



@user_router.post("/redeem-invite/{token}", status_code=status.HTTP_200_OK)
async def redeem_invite(token: str, missingCreds: UserMissingCredentials, uow: UnitOfWork = Depends(get_uow)):

    tokenizer = URLTokenizer(TokenType.INVITATION, 1000) # TODO: remove time limit 1000
    token_data = tokenizer.decode_url_safe_token(token)    

    user_data = UserCreate(**(missingCreds.model_dump()), **(token_data))

    async with uow:
        user_service = UserService(uow)
        user = await user_service.create_user(user_data)
        user.is_verified = True



@user_router.get("/confirm-email/{token}", status_code=status.HTTP_200_OK)
async def confirm_email(token: str, request: Request, response: Response, uow: UnitOfWork = Depends(get_uow)):   

    tokenizer = URLTokenizer(TokenType.CONFIRMATION)
    token_data = tokenizer.decode_url_safe_token(token)

    async with uow:
        user_service = UserService(uow)

        user = await user_service.get_user_by_email(token_data.get("email"))
        if not user.is_verified:
            await user_service.update_user(user, {"is_verified": True})

            return templates.TemplateResponse(
                "verified.html",
                {
                    "request":request,
                    "message": "Your account has been succesfully verified"
                }
            )


@user_router.post("/sign-in")
async def sign_in(user_data: UserLogin, response: Response, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(user_data.email)

        password_match = verify_hash(user_data.password, user.password_hash)
        if password_match:
            access_token = await user_service.generate_auth_tokens(user, response)

            return access_token


@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserGet)
async def get_me(curr_user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    return JSONResponse(
        content = {
        "username": curr_user.username,
        "email": curr_user.email,
        "role": str(curr_user.role.role),
        "doc_count": curr_user.doc_count
        })

        

@user_router.post("/refresh")
async def refresh_tokens(request: Request, response: Response, refresh_jwt: dict = Security(RefreshCookieBearer()), uow: UnitOfWork = Depends(get_uow)):

    token = refresh_jwt['token']
    data = refresh_jwt['data']

    async with uow:
        user_service = UserService(uow)
        user = await user_service.get_user_by_email(data['user']['email'])
        if user and verify_hash(token, user.refresh_jwt_hash):
            access = await user_service.generate_auth_tokens(user, response)
            return {"access_token":access}
