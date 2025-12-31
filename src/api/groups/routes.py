







from src.api.users.service import UserService
from src.api.users.schemas import UserCreate
from src.api.groups.service import GroupService
from src.api.groups.schemas import GroupCreate, GroupGet
from src.core.db.models import UserRole
from src.core.db.unit_of_work import UnitOfWork, get_uow

from src.core.utils.mail_manager import MailManager, get_mail_man, EmailType
from src.core.utils.url_tokenizer import URLTokenizer, TokenType
from src.errors.exceptions import NotFoundError 

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks, UploadFile, Form
from pydantic import NameEmail


group_router = APIRouter()

@group_router.post("/create-group", status_code=status.HTTP_201_CREATED)
async def create_group(request: Request, background_tasks: BackgroundTasks,
                       group_data_json: str = Form(...), user_data_json: str = Form(...), 
                       group_picture: UploadFile | None = None , uow: UnitOfWork = Depends(get_uow),
                       mail_man: MailManager = Depends(get_mail_man)):
    
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
                tokenizer = URLTokenizer(TokenType.CONFIRMATION)

                link = tokenizer.get_tokenized_link({"email":user.email})

                await mail_man.send_templated_email({"username":user.username, "link":link}, 
                                                           [user_data.email], EmailType.CONFIRMATION, 
                                                           background_tasks)

                return JSONResponse(content="Group succesfully created. Check your e-mail to confirm the account")
            

@group_router.get("/my-group", status_code=status.HTTP_200_OK, response_model=GroupGet)
async def get_group(group_uid: str, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        group_service = GroupService(uow)
        group = await group_service.get_group_by_uid(group_uid)

        if group is not None: 
                return group
        raise NotFoundError
