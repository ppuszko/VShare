from fastapi import APIRouter, Depends, status
from src.api.groups.service import GroupService
from src.api.users.service import UserService
from src.api.users.schemas import UserCreate
from .schemas import GroupCreate, GroupGet
from src.core.db.models import UserRole
from src.core.unit_of_work import UnitOfWork, get_uow
from src.core.mail import send_mail_background, generate_confirmation_template
from src.core.config import Config
from src.errors.exceptions import NotFoundError 
from src.auth.utils import create_url_safe_token, decode_url_safe_token

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks, UploadFile, Form
from pydantic import NameEmail
group_router = APIRouter()

@group_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_group(request: Request, background_tasks: BackgroundTasks,
                       group_data_json: str = Form(...), user_data_json: str = Form(...), 
                       group_picture: UploadFile | None = None , uow: UnitOfWork = Depends(get_uow)
                       ):
    
    group_data = GroupCreate.model_validate_json(group_data_json)
    user_data = UserCreate.model_validate_json(user_data_json)

    async with uow:
        group_service = GroupService(uow)
        user_service = UserService(uow)

        #TODO implement picture saving

        group = await group_service.create_group(group_data)
        if group is not None:
            user_data.role = UserRole.ADMIN
            user_data.group_uid = str(group.uid)
            user = await user_service.create_user(user_data)

            if user is not None:
                token = create_url_safe_token({"email":user_data.email}, request.app.state.verify_email_serializer)
                body = generate_confirmation_template(user_data.username, f"http://{Config.DOMAIN}/users/confirm-email/{token}")
                recipients = [NameEmail("", user_data.email)]
                await send_mail_background(Config.CONFIRM_MAIL_SUBJECT, recipients, body, request, background_tasks)

                return JSONResponse(content="Group succesfully created. Check your e-mail to confirm the account")
            

@group_router.get("/my-group", status_code=status.HTTP_200_OK, response_model=GroupGet)
async def get_group(group_uid: str, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        group_service = GroupService(uow)
        group = await group_service.get_group_by_uid(group_uid)

        if group is not None: 
                return group
        raise NotFoundError
