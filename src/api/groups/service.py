from src.core.db.models import Group
from src.core.unit_of_work import UnitOfWork
from sqlmodel import select, delete
from src.errors.exceptions import NotFoundError, ForbiddenError
from src.errors.decorators import handle_exceptions
from .schemas import GroupCreate


class GroupService:

    def __init__(self, uow: UnitOfWork):
        self._session = uow.get_session

    @handle_exceptions
    async def get_group_by_name(self, group_name: str) -> Group | None:
        group = (await self._session.exec(select(Group).where(Group.name == group_name))).one_or_none()
        return group
        
    @handle_exceptions
    async def get_group_by_uid(self, group_uid: str) -> Group | None:
        group = (await self._session.exec(select(Group).where(Group.uid == group_uid))).one_or_none()
        return group

    async def group_exist(self, group_name: str) -> bool:
        return await self.get_group_by_name(group_name) is not None

    @handle_exceptions
    async def create_group(self, group_data: GroupCreate) -> Group | None:
        if not (await self.group_exist(group_data.name)):
            new_group = Group(**(group_data.model_dump()))
            self._session.add(new_group)
            return new_group
        raise ForbiddenError(detail="There is already a group registered under this name!")