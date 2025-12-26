from fastapi import APIRouter, Depends, UploadFile, Security
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from redis.asyncio import Redis

from src.core.utils.caching_service import CachingService, get_redis

from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.api.users.schemas import UserGet
from src.api.vectors.schemas import QueryFilters, DocumentAdd

from src.api.vectors.service import VectorService
from src.api.users.service import UserService
from src.core.utils.file_service import FileService
from src.core.utils.url_tokenizer import URLTokenizer, TokenType
from src.core.config.file import FileConfig

from src.auth.dependencies import RoleChecker

from src.core.inference.tasks import compute_and_insert_embeddings


vector_router = APIRouter()


@vector_router.post("/upload")
async def upload_data(files: list[UploadFile], 
                      metadata: list[DocumentAdd],
                      user: UserGet = Security(RoleChecker(["USER", "ADMIN"])), 
                      uow: UnitOfWork = Depends(get_uow),
                      redis_instance: Redis = Depends(get_redis)):
    
    if len(files) != len(metadata):
        raise Exception("Amount of files doesn't match amount of associated metadata!")

    fs = FileService(str(user.group.uid), FileConfig.STORAGE_PATH)
    documents = [fs.save_file(file) for file in files]

    async with uow:
        user_service = UserService(uow)
        files_to_embed = await user_service.add_documents(documents, metadata, user)

    tokenizer = URLTokenizer(TokenType.EMBEDDING_REPORT)
    user_data = {"user_uid": str(user.uid)}
    ticket = tokenizer.create_url_safe_token(user_data)
    url = tokenizer.get_tokenized_link(user_data)

    cache = CachingService(redis_instance)
    await cache.insert_ticket(ticket)

    compute_and_insert_embeddings.delay(files_to_embed, url)
        
    
@vector_router.post("/embedding-report/{ticket}")
async def embedding_report(ticket: str, redis_instance: Redis = Depends(get_redis)):
    tokenizer = URLTokenizer(TokenType.EMBEDDING_REPORT)
    cache = CachingService(redis_instance)
    process_ticket = await cache.should_process_ticket(ticket)

    if process_ticket:
        tokenizer.decode_url_safe_token(ticket)
        # TODO: implement user notification



@vector_router.get("/search")
async def search(query: str, query_filters: QueryFilters, user: UserGet = Security(RoleChecker(["USER", "ADMIN"]))):
    pass