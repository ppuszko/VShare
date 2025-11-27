from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Group
from sqlmodel import select, delete
from src.errors.exceptions import NotFoundError, ForbiddenError
from src.errors.decorators import handle_exceptions
from .schemas import GroupCreate


class GroupService:
    @handle_exceptions
    async def get_group_by_name(self, group_name: str, session: AsyncSession) -> Group | None:
        group = (await session.exec(select(Group).where(Group.name == group_name))).first()
        if group is None:
            raise NotFoundError
        else:
            return group
        
    @handle_exceptions
    async def get_group_by_uid(self, group_uid: str, session: AsyncSession) -> Group | None:
        group = (await session.exec(select(Group).where(Group.uid == group_uid))).first()
        if group is None:
            raise NotFoundError
        else:
            return group

    async def group_exist(self, group_name: str, session: AsyncSession) -> bool:
        return (await session.exec(select(Group).where(Group.name == group_name))).first() is not None

    @handle_exceptions
    async def create_group(self, group_data: GroupCreate, session: AsyncSession) -> Group | None:
        if not (await self.group_exist(group_data.name, session)):
            new_group = Group(**(group_data.model_dump()))
            session.add(new_group)
            await session.commit()
            return new_group
        raise ForbiddenError(detail="There is already a group registered under this name!")