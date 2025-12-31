from fastapi import APIRouter, Depends, UploadFile, Security
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks

from src.core.utils.cache_manager import CacheManager, get_cache_manager

from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.api.users.schemas import UserGet
from src.api.vectors.schemas import QueryFilters, DocumentAdd
from src.api.vectors.service import VectorService, get_querying_vector_service

from src.api.users.service import UserService
from src.core.utils.file_manager import FileManager, get_file_man
from src.core.utils.mail_manager import MailManager, EmailType, get_mail_man
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
                      cache_manager: CacheManager = Depends(get_cache_manager),
                      file_man: FileManager = Depends(get_file_man)):
    
    if len(files) != len(metadata):
        raise Exception("Amount of files doesn't match amount of associated metadata!")

    group_uid = str(user.group.uid)
    documents = [file_man.save_file(file, group_uid) for file in files]

    async with uow:
        user_service = UserService(uow)
        files_to_embed = await user_service.add_documents(documents, metadata, user)

    tokenizer = URLTokenizer(TokenType.EMBEDDING_REPORT)
    user_data = {"user_uid": str(user.uid),
                 "user_email": user.email,
                 "username": user.username}
    ticket = tokenizer.create_url_safe_token(user_data)
    url = tokenizer.get_tokenized_link(user_data)

    await cache_manager.insert_ticket(ticket)

    compute_and_insert_embeddings.delay(files_to_embed, url)
        
    
@vector_router.post("/embedding-report/{ticket}")
async def embedding_report(ticket: str, body: dict, 
                           background_tasks: BackgroundTasks, 
                           cache_manager: CacheManager = Depends(get_cache_manager), 
                           mail_man: MailManager = Depends(get_mail_man)):
    
    tokenizer = URLTokenizer(TokenType.EMBEDDING_REPORT)
    process_ticket = await cache_manager.should_process_ticket(ticket)

    if process_ticket:
        user_data = tokenizer.decode_url_safe_token(ticket)
        recipients = [user_data["user_email"]]
        body["username"] = user_data["username"]
        await mail_man.send_templated_email(body, recipients, EmailType.EMBEDDING_REPORT, background_tasks)


@vector_router.get("/search")
async def search(query: str, query_filters: QueryFilters, 
                 user: UserGet = Security(RoleChecker(["USER", "ADMIN"])), 
                 vector_service: VectorService = Depends(get_querying_vector_service)):

    res = await vector_service.query_db(query_filters, query)