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
    
    if len(files) != len(metadata):
        raise Exception("Amount of files doesn't match amount of associated metadata!")

    fs = FileService(str(user.group.uid), FileConfig.STORAGE_PATH)
    processed_documents = [fs.save_file(file) for file in files]
    data_to_embedd = []

    async with uow:
        user_service = UserService(uow)

        for file, meta in zip(processed_documents, metadata):
            if file is not None:
                meta.group_uid = user.group.uid
                meta.user_uid = user.uid
                meta.storage_path = file

                payload = await user_service.add_document(meta)

                data_to_embedd.append(payload)
            else:
                data_to_embedd.append(meta)

    


@vector_router.get("/search")
async def search(query: str, query_filters: QueryFilters, user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass