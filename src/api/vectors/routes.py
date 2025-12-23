from fastapi import APIRouter, Depends, UploadFile, Security
from fastapi.responses import JSONResponse
from fastapi.requests import Request

import time

from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.api.users.schemas import UserGet
from src.api.vectors.schemas import QueryFilters, DocumentAdd

from src.api.vectors.service import VectorService
from src.api.users.service import UserService
from src.core.utils.file_service import FileService
from src.core.config.file import FileConfig

from src.auth.dependencies import RoleChecker



vector_router = APIRouter()


@vector_router.post("/upload")
async def upload_data(files: list[UploadFile], 
                      metadata: list[DocumentAdd],
                      user: UserGet = Security(RoleChecker(["USER", "ADMIN"])), 
                      uow: UnitOfWork = Depends(get_uow)):
    fs = FileService(FileConfig.STORAGE_PATH)
    saved, failed = fs.save_files(files, metadata)

    payload_data = []
    async with uow:

        user_service = UserService(uow)

        for s, m in saved:
            m.group_uid = user.group.uid
            m.user_uid = user.uid
            m.storage_path = s

            doc = await user_service.add_document(m)
            payload_data.append(doc)


    


@vector_router.get("/search")
async def search(query: str, query_filters: QueryFilters, user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass