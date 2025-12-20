from fastapi import APIRouter, Depends, UploadFile, Security
from fastapi.responses import JSONResponse
from fastapi.requests import Request

import time

from src.api.users.schemas import UserGet
from src.api.vectors.schemas import QueryFilters, DocumentAdd
from src.core.vector.service import VectorService
from src.tools.file_service import FileService
from src.core.config.file import FileConfig

from src.auth.dependencies import RoleChecker

from pympler import asizeof

vector_router = APIRouter()

@vector_router.post("/test")
async def test(files: list[UploadFile], request: Request):
    fs = FileService(FileConfig.PICTURE_STORAGE_PATH)

    start = time.perf_counter()
    success, fail = fs.save_files(files)
    
    text_to_process = []
    for s in success:
        text_to_process.append(fs.extract_text_from_files(s))

    vector = VectorService(request)
    size = vector.compute_vectors(text_to_process)

    end = time.perf_counter()

    return JSONResponse(content={"time in seconds": (end - start), "failed": fail, "success": success, "size of embeddings": size})



@vector_router.post("/upload")
async def upload_data(files: list[UploadFile], user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass


@vector_router.get("/search")
async def search(query: str, query_filters: QueryFilters, user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass