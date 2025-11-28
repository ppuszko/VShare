from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import GroupService
from src.auth.service import UserService
from .schemas import GroupCreate, GroupGet
from src.db.main import get_session
from src.errors.decorators import handle_exceptions

group_service = GroupService()
user_service = UserService()

group_router = APIRouter()

@group_router.post('/create', status_code=status.HTTP_201_CREATED, response_model=GroupGet)
async def create_group(group_data: GroupCreate, session: AsyncSession = Depends(get_session)):
    group = await group_service.create_group(group_data, session)
    if group is not None:
        return GroupGet(**(group.model_dump()))
    

@group_router.get("/my-group", status_code=status.HTTP_200_OK, response_model=GroupGet)
async def get_group(group_uid: str, session: AsyncSession = Depends(get_session)):
    group = await group_service.get_group_by_uid(group_uid, session)
    if group is not None: 
        return group
    
