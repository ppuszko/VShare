from sqlalchemy import select

from src.core.db.unit_of_work import UnitOfWork
from src.core.db.models import Document
from src.api.documents.schemas import DocumentAdd, DocumentGet
from src.api.users.schemas import UserGet

from src.errors.exceptions import NotFoundError


class DocumentService:

    def __init__(self, uow: UnitOfWork):
        self._session = uow.session


    async def add_documents(self, documents: list[str | None], documents_metadata: list[DocumentAdd], user: UserGet) -> tuple[list[DocumentAdd], int]:
        saved_docs = []
        doc_count = 0

        for file, meta in zip(documents, documents_metadata):
            if file is not None:
                doc_count += 1
                
                meta.group_uid = user.group.uid
                meta.user_uid = user.uid
                meta.storage_path = file

                db_doc = Document(**(meta.model_dump()))
                self._session.add(db_doc)

                saved_docs.append(db_doc)
            else:
                saved_docs.append(meta)

        if doc_count != 0:
            await self._session.flush()
        return [DocumentAdd(**(doc.model_dump())) for doc in saved_docs], doc_count


    async def extend_document_metadata(self, documents: list[dict]) -> list[dict]:
        doc_ids = set(item["doc_id"] for item in documents)
        result = await self._session.exec(select(Document).where(Document.id.in_(doc_ids)))  # type: ignore[arg-type]
        result = result.scalars().all()
        if not result:
            raise NotFoundError
        
        docs_from_db = {item.id : {"title": item.title, "storage_path": item.storage_path} for item in result} 
        
        for i, doc in enumerate(documents):
            doc_id = doc["doc_id"]
            documents[i].update(docs_from_db[doc_id])

        return documents