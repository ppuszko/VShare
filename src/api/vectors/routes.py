from pydantic import TypeAdapter

from fastapi import APIRouter, Depends, UploadFile, Security, Form, File
from fastapi import BackgroundTasks

from src.api.documents.service import DocumentService
from src.api.documents.schemas import DocumentAdd
from src.api.users.service import UserService
from src.api.groups.service import GroupService
from src.core.db.unit_of_work import UnitOfWork, get_uow
from src.api.users.schemas import UserGet
from src.api.vectors.schemas import QueryFilters
from src.api.vectors.service import VectorService, get_querying_vector_service
from src.core.inference.tasks import compute_and_insert_embeddings

from src.core.utils.file_manager import FileManager, get_file_man
from src.core.utils.mail_manager import MailManager, EmailType, get_mail_man
from src.core.utils.cache_manager import CacheManager, get_cache_manager
from src.core.utils.url_tokenizer import URLTokenizer, TokenType

from src.auth.dependencies import RoleChecker

from src.errors.exceptions import BadRequest


vector_router = APIRouter()


@vector_router.post("/upload")
async def upload_data(files: list[UploadFile] = File(...), 
                      metadata_list: str = Form(...),
                      user: UserGet = Security(RoleChecker(["USER", "ADMIN"])), 
                      uow: UnitOfWork = Depends(get_uow),
                      cache_manager: CacheManager = Depends(get_cache_manager),
                      file_man: FileManager = Depends(get_file_man)):
    
    metadata = TypeAdapter(list[DocumentAdd]).validate_json(metadata_list)

    if len(files) != len(metadata):
        raise BadRequest("Amount of files doesn't match amount of associated metadata!")

    group_uid = str(user.group.uid)
    documents = [file_man.save_file(file, group_uid) for file in files]

    async with uow:
        user_service = UserService(uow)
        doc_service = DocumentService(uow)
        files_to_embed, doc_count = await doc_service.add_documents(documents, metadata, user)
        await user_service.update_doc_count(doc_count, str(user.uid))

        tokenizer = URLTokenizer(TokenType.EMBEDDING_REPORT)
        user_data = {"user_uid": str(user.uid),
                    "user_email": user.email,
                    "username": user.username}
        ticket = tokenizer.create_url_safe_token(user_data)
        url = tokenizer.get_tokenized_link(user_data)


        await cache_manager.insert_ticket(ticket)

    files_to_embed_dicts = [file.model_dump(mode="json") for file in files_to_embed]
    compute_and_insert_embeddings.delay(files_to_embed_dicts, url)


    
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
async def search(query: str, query_filters: str, 
                 user: UserGet = Security(RoleChecker(["USER", "ADMIN"])), 
                 vector_service: VectorService = Depends(get_querying_vector_service),
                 uow: UnitOfWork = Depends(get_uow)):
    
    filters = QueryFilters.model_validate_json(query_filters)
    filters.group_uid = user.group.uid
    if filters.only_my_articles:
                filters.user_uid = user.uid

    query_res = await vector_service.query_db(filters, query)
    async with uow:
        doc_service = DocumentService(uow)
        
        query_res = await doc_service.extend_document_metadata(query_res)

    return query_res


@vector_router.get("/fetch-categories")
async def fetch_group_categories(curr_user: UserGet = Security(RoleChecker(["ADMIN", "USER"])), 
                                 uow: UnitOfWork = Depends(get_uow),
                                 cache_man: CacheManager = Depends(get_cache_manager)):
    group_uid = str(curr_user.group.uid)
    group_categories = await cache_man.get_cached_categories(group_uid)

    if not bool(group_categories):
        async with uow:
            group_service = GroupService(uow)
            group_categories = await group_service.get_group_categories(group_uid)

        await cache_man.set_cached_categories(group_uid, group_categories) 

    return group_categories