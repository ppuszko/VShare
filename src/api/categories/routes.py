from fastapi import APIRouter, Depends, Security

from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.core.utils.cache_manager import CacheManager, get_cache_manager

from src.api.categories.service import CategoryService
from src.api.categories.schemas import CategoryUpdate
from src.api.users.schemas import UserGet

from src.auth.dependencies import RoleChecker


cat_router = APIRouter()


@cat_router.get("/fetch-categories")
async def fetch_group_categories(curr_user: UserGet = Security(RoleChecker(["ADMIN", "USER"])), 
                                 uow: UnitOfWork = Depends(get_uow),
                                 cache_man: CacheManager = Depends(get_cache_manager)):
    group_uid = str(curr_user.group.uid)
    group_categories = await cache_man.get_cached_categories(group_uid)

    if not bool(group_categories):
        async with uow:
            cat_service =  CategoryService(uow)
            group_categories = await cat_service.get_group_categories(group_uid)

        await cache_man.set_cached_categories(group_uid, group_categories) 

    return group_categories


@cat_router.get("/delete-category")
async def delete_category(cat_id: int, curr_user: UserGet = Security(RoleChecker(["ADMIN"])),
                       uow: UnitOfWork = Depends(get_uow), cache_man: CacheManager = Depends(get_cache_manager)):
    async with uow:
        cat_service = CategoryService(uow)
        await cat_service.delete_category(curr_user.group.uid, cat_id)
        await cache_man.delete_cached_category(str(curr_user.group.uid), cat_id)


@cat_router.post("/add-category")
async def add_category(cat_name: str, curr_user: UserGet = Security(RoleChecker(["ADMIN"])),
                       uow: UnitOfWork = Depends(get_uow), cache_man: CacheManager = Depends(get_cache_manager)):
    async with uow:
        cat_service = CategoryService(uow)
        new_cat = await cat_service.add_category(curr_user.group.uid, cat_name)
        await cache_man.add_or_update_cached_category(str(curr_user.group.uid), new_cat)


@cat_router.post("/update-category")
async def update_category(cat_update: CategoryUpdate, curr_user: UserGet = Security(RoleChecker(["ADMIN"])),
                       uow: UnitOfWork = Depends(get_uow), cache_man: CacheManager = Depends(get_cache_manager)):
    async with uow:
        cat_service = CategoryService(uow)
        updated_cat = await cat_service.update_category(curr_user.group.uid, cat_update)
        await cache_man.add_or_update_cached_category(str(curr_user.group.uid), updated_cat)