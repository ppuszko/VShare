from fastapi import APIRouter, Depends, UploadFile, Security


from src.api.users.schemas import UserGet
from .schemas import QueryFilters

from src.auth.dependencies import RoleChecker


vectors_router = APIRouter()



@vectors_router.post("/upload")
async def upload_data(files: list[UploadFile], user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass


@vectors_router.get("/search")
async def search(query: str, query_filters: QueryFilters, user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass