from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Document, Embedding
from sqlmodel import select, desc, delete
from .schemas import DocUpload
from tools import processing
from pathlib import Path



class FileService:
    async def get_user_docs(self, user_uid: str, session: AsyncSession):
        result = await session.exec(select(Document).where(Document.uid == user_uid).order_by(desc(Document.created_at)))
        return result.all()
    
    async def get_doc(self, doc_uid: str, session: AsyncSession):
        doc = await session.exec(select(Document).where(Document.uid == doc_uid))
        return doc.first() 
    
    async def create_doc(self, doc_data: DocUpload, user_uid: str, session: AsyncSession):
        new_file_path = await processing.save_file(doc_data.file)
        is_public = doc_data.is_public

        new_file = Document(path_to_document=new_file_path, user_uid=user_uid, is_public=is_public, doc_title=doc_data.doc_title)
        session.add(new_file)

        await self._create_embeddings(new_file_path, new_file.uid, session)

    async def delete_doc(self, doc_uid: str, session: AsyncSession):
        doc_to_delete = await self.get_doc(doc_uid, session)
        if doc_to_delete is not None:
            await self._delete_embeddings(doc_uid, session)
            await session.delete(doc_to_delete)
            await session.commit()
            return {}
        return None

    async def _create_embeddings(file_path: str | Path, doc_uid: str, session: AsyncSession):
        file_text = processing.extract_pdf(file_path)
        chunks = processing.create_chunks(file_text)

        for chunk in chunks:
            embedding = processing.create_embedding(chunk)
            new_embedding = Embedding(document_uid=doc_uid, embedding_vector=embedding, chunk_str=chunk)
            session.add(new_embedding)

        await session.commit()


    async def _delete_embeddings(doc_uid: str, session: AsyncSession):
        await session.exec(delete(Embedding).where(Embedding.document_uid == doc_uid))
        await session.commit()
       


