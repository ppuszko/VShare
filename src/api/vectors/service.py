from collections.abc import Iterator
import itertools

from qdrant_client import models, AsyncQdrantClient, QdrantClient
from fastembed import  TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid6 import uuid7

from src.api.vectors.schemas import  DocumentAdd
from src.core.config.vector import VectorConfig


class VectorService:

    def __init__(
            self, 
            dense_model: TextEmbedding,
            sparse_model: SparseTextEmbedding, 
            multi_model: LateInteractionTextEmbedding, 
            client: AsyncQdrantClient | QdrantClient
    ):
        self._dense = dense_model
        self._sparse = sparse_model
        self._multi = multi_model
        self._client = client
        self._failed = []


    def upload_embeddings(self, documents: Iterator[tuple[str | None, DocumentAdd]]):
        if not isinstance(self._client, QdrantClient):
            return
        
        self._client.upload_points(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            points=self._points_generator(documents))

 
    def _points_generator(self, documents: Iterator[tuple[str | None, DocumentAdd]]):
        for doc, metadata in documents:
            if doc is None:
                self._failed.append(metadata.title)
                continue

            chunks = self._construct_chunks(doc)
            dense_iter = self._dense.query_embed(chunks)
            sparse_iter = self._sparse.embed(chunks)
            multi_iter = self._multi.embed(chunks)

            for chunk, dense, sparse, multi in zip(chunks, dense_iter, sparse_iter, multi_iter):
                yield models.PointStruct(
                    id=uuid7(),
                    payload = {"group_uid":metadata.group_uid,
                        "user_uid":metadata.user_uid,
                        "created_at":metadata.created_at,
                        "category_id":metadata.category_id,
                        "chunk_text":chunk},
                    vector={
                        "dense":dense,
                        "sparse":sparse.as_object(),
                        "multi":multi
                    } # type: ignore
                )

    def _construct_chunks(self, doc: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        return splitter.split_text(doc)
    

    def report(self) -> list[int]:
        return self._failed


        


    
                
