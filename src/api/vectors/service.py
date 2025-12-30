from collections.abc import Iterator
import asyncio

from fastapi import Depends
from qdrant_client import models, AsyncQdrantClient, QdrantClient
from qdrant_client.http.models import QueryResponse
from fastembed import  TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from numpy import ndarray
from uuid6 import uuid7

from src.api.vectors.schemas import  DocumentAdd, QueryFilters
from src.api.vectors.main import get_querying_client_components
from src.core.config.vector import VectorConfig


def get_querying_vector_service(args: tuple = Depends(get_querying_client_components)):
    return VectorService(*args)


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
        self._documents = []
        self._emb_counts = []


    def upload_embeddings(self, documents: Iterator[tuple[str | None, DocumentAdd]])  -> tuple[list[int | None], list[int | None]]:
        if isinstance(self._client, QdrantClient):
            self._client.upload_points(
                collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
                points=self._points_generator(documents))

        return self._report()


    async def query_db(self, filters: QueryFilters, query: str):
        if not isinstance(self._client, AsyncQdrantClient):
            raise TypeError("Vector Service initialized with QdrantClient instead of AsyncQdrantClient")
        global_filter = self._build_filter(filters)
        
        dense_query, sparse_query, multi_query = await self._get_query_embeddings(query)

        hybrid_query = [
            models.Prefetch(query=dense_query.tolist(), using="dense", limit=100),
            models.Prefetch(query=models.SparseVector(**sparse_query), using="sparse", limit=100)
        ]

        fusion_query = models.Prefetch(
            prefetch=hybrid_query,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=100
        )

        response = await self._client.query_points(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            prefetch=fusion_query,
            query=multi_query,
            using="multi",
            query_filter=global_filter,
            limit=10,
            with_payload=True
        )

        return self._process_retrieved_data(response)


    def _build_filter(self, filters: QueryFilters) -> models.Filter:
        field_conditions: list[models.Condition] = [
            models.FieldCondition(
                key="group_uid",
                match=models.MatchValue(value=str(filters.group_uid))
            ),
            models.FieldCondition(
                key="created_at",
                range=models.DatetimeRange(
                    gte=filters.time_frame[0],
                    lte=filters.time_frame[1])
            ),
            ]

        if filters.category_id is not None:
            field_conditions.append(models.FieldCondition(
                key="category_id",
                match=models.MatchAny(any=filters.category_id)
            ))
        if filters.user_uid is not None:
            field_conditions.append(models.FieldCondition(
                key="user_uid",
                match=models.MatchValue(value=str(filters.user_uid))
            ))
        
        return models.Filter(
            must=field_conditions
        )


    async def _get_query_embeddings(self, query: str) -> tuple[ndarray, dict, ndarray]:
        def _helper(query):
            dense = next(iter(self._dense.query_embed(query)))
            sparse = next(iter(self._sparse.query_embed(query))).as_object()
            multi = next(iter(self._multi.query_embed(query))) 
            return dense, sparse, multi
        
        return await asyncio.to_thread(_helper, query)


    def _process_retrieved_data(self, response: QueryResponse) -> list[dict]:
        processed = []

        for i, item in enumerate(response.points or [], 1):
            payload = item.payload
            if payload is None: continue
            processed.append({
                "rank":i,
                "contents": payload["chunk_text"],
                "created_at":payload["created_at"],
                "category_id":payload["category_id"],
                "owner_uid":payload["user_uid"]
            })
        
        return processed

    def _points_generator(self, documents: Iterator[tuple[str | None, DocumentAdd]]) -> Iterator[models.PointStruct]:
        for doc, metadata in documents:
            if doc is None:
                self._emb_counts.append(0)
                continue

            chunks = self._construct_chunks(doc)
            dense_iter = self._dense.query_embed(chunks)
            sparse_iter = self._sparse.query_embed(chunks)
            multi_iter = self._multi.query_embed(chunks)
            self._emb_counts.append(len(chunks))
            
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
            
            self._documents.append(metadata.title)

    def _construct_chunks(self, doc: str) -> list[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        return splitter.split_text(doc)
    

    def _report(self) -> tuple[list[int | None], list[int | None]]:
        return self._documents, self._emb_counts


        


    
                
