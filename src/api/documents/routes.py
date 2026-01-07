from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.auth.dependencies import RoleChecker
from src.api.users.schemas import UserGet

from src.core.config.file import FileConfig
from src.errors.exceptions import NotFoundError


doc_router = APIRouter()


@doc_router.get("/download/{filename}")
async def download(filename: str, user: UserGet = Depends(RoleChecker(["ADMIN", "USER"]))):
    file_path = Path(f"{FileConfig.STORAGE_PATH}/{user.group.uid}/{filename}")

    if not file_path.exists():
        raise NotFoundError("Sorry, the file you are looking for does not exist!")
    
    return FileResponse(path=file_path,
                        filename=file_path.name,
                        content_disposition_type="inline")