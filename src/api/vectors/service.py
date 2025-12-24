from collections.abc import Iterator
import itertools

from qdrant_client import models, AsyncQdrantClient, QdrantClient
from fastembed import  TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.api.vectors.schemas import  DocumentAdd


class VectorService:

    def __init__(
            self, 
            dense_model: TextEmbedding,
            sparse_model: SparseTextEmbedding, 
            multi_model: LateInteractionTextEmbedding, 
            client: AsyncQdrantClient | QdrantClient
    ):
        self.dense = dense_model
        self.sparse = sparse_model
        self.multi = multi_model
        self.client = client


    def upload_embeddings(self, documents: list[tuple[str | None, DocumentAdd]]):
        if not isinstance(self.client, QdrantClient):
            return

        payload_iter = iter(())
        dense_iter = iter(())
        sparse_iter = iter(())
        multi_iter = iter(())

        encoded = []
        failed = []

        for doc, metadata in documents:
            if doc is None:
                failed.append(metadata.title)
                continue
            
            chunks, payload = self._construct_chunks_and_payload(doc, metadata)
            dense_iter =  itertools.chain(dense_iter, self.dense.embed(chunks))
            sparse_iter = itertools.chain(sparse_iter, self.sparse.embed(chunks))
            multi_iter = itertools.chain(multi_iter, self.multi.embed(chunks))
            payload_iter = itertools.chain(payload_iter, payload)

            encoded.append(metadata.title)


    def _construct_chunks_and_payload(self, doc: str, metadata: DocumentAdd) -> tuple[list[str], Iterator]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = splitter.split_text(doc)
        payloads = (
            {"group_uid":metadata.group_uid,
             "user_uid":metadata.user_uid,
             "created_at":metadata.created_at,
             "category_id":metadata.category_id,
             "chunk_text":chunk
            } for chunk in chunks )
        
        return chunks, payloads

        


    
                
