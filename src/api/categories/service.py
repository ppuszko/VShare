from sqlmodel import select
from uuid import UUID

from src.core.db.unit_of_work import UnitOfWork
from src.core.db.models import Category

from src.errors.exceptions import NotFoundError, BadRequest

from src.api.categories.schemas import CategoryGet, CategoryUpdate


class CategoryService:

    def __init__(self, uow: UnitOfWork):
        self._session = uow.session

    async def get_group_categories(self, group_uid: str) -> dict:
        group_categories = (await self._session.exec(select(Category).where(Category.group_uid == group_uid))).all()
        default_categories = (await self._session.exec(select(Category).where(Category.group_uid == None))).all()
        
        categories = {cat.id : cat.name for cat in group_categories}
        categories.update(
            {cat.id : cat.name for cat in default_categories}
        )

        return categories
    

    async def _get_category(self, group_uid: UUID, cat_id: int) -> Category:
        res = await self._session.exec(select(Category).where(Category.group_uid == group_uid, 
                                                              Category.id == cat_id))
        cat = res.one_or_none()
        if cat is None:
            raise NotFoundError
        return cat
    
    
    async def _check_category_exist_by_name(self, group_uid: UUID, cat_name: str) -> bool:
        res = await self._session.exec(select(Category).where(Category.group_uid == group_uid,
                                                              Category.name == cat_name))
        return res.one_or_none() is not None


    async def add_category(self, group_uid: UUID, cat_name: str):
        if await self._check_category_exist_by_name(group_uid, cat_name):
            raise BadRequest(f"Category {cat_name} already exists!")
        
        new_cat = Category(name=cat_name, group_uid=group_uid)
        self._session.add(new_cat)
        await self._session.flush()
        return CategoryGet(**(new_cat).model_dump())


    async def update_category(self, group_uid: UUID, cat_update: CategoryUpdate) -> CategoryGet:
        cat = await self._get_category(group_uid, cat_update.id)

        cat.name = cat_update.new_name
        return CategoryGet(**(cat).model_dump())
    

    async def delete_category(self, group_uid: UUID, cat_id: int):
        cat = await self._get_category(group_uid, cat_id)
        await self._session.delete(cat)