from src.core.db.models import Group, Category
from src.core.db.unit_of_work import UnitOfWork
from sqlmodel import select
from src.errors.exceptions import NotFoundError, ForbiddenError

from .schemas import GroupCreate


class GroupService:

    def __init__(self, uow: UnitOfWork):
        self._session = uow.session

    async def get_group_by_name(self, group_name: str) -> Group:
        group = await self._session.exec(select(Group).where(Group.name == group_name))
        result = group.one_or_none()

        if result is None:
            raise NotFoundError
        
        return result
        

    async def get_group_by_uid(self, group_uid: str) -> Group:
        group = await self._session.exec(select(Group).where(Group.uid == group_uid))
        result = group.one_or_none()

        if result is None:
            raise NotFoundError
        
        return result

    async def group_exist(self, group_name_or_uid: str) -> bool:
        by_uid = (await self._session.exec(select(Group).where(Group.uid == group_name_or_uid))).one_or_none() is not None
        by_name = (await self._session.exec(select(Group).where(Group.name == group_name_or_uid))).one_or_none() is not None

        return by_uid or by_name

    async def create_group(self, group_data: GroupCreate) -> Group:
        if not (await self.group_exist(group_data.name)):
            new_group = Group(**(group_data.model_dump()))
            self._session.add(new_group)
            return new_group
        raise ForbiddenError(detail="There is already a group registered under this name!")
    

    async def get_group_categories(self, group_uid: str) -> dict:
        if not await self.group_exist(group_uid):
            raise NotFoundError
        
        group_categories = (await self._session.exec(select(Category).where(Category.group_uid == group_uid))).all()
        default_categories = (await self._session.exec(select(Category).where(Category.group_uid == None))).all()
        
        categories = {cat.id : cat.name for cat in group_categories}
        categories.update(
            {cat.id : cat.name for cat in default_categories}
        )

        return categories