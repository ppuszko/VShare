import asyncio

from qdrant_client import models, AsyncQdrantClient, QdrantClient
from fastembed import TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from fastapi import Request, Depends

from src.core.config.vector import VectorConfig

def init_client() -> QdrantClient:
    return QdrantClient(url=VectorConfig.VECTOR_DB_URL)

def init_async_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=VectorConfig.VECTOR_DB_URL)

def load_dense_model() -> TextEmbedding:
    return TextEmbedding(VectorConfig.DENSE_MODEL, device="cpu")

def load_sparse_model() -> SparseTextEmbedding:
    return SparseTextEmbedding(VectorConfig.SPARSE_MODEL)

def load_multivector_model() -> LateInteractionTextEmbedding:
    return LateInteractionTextEmbedding(VectorConfig.MULTI_MODEL)

def get_querying_client_components(request: Request) -> tuple:
    return (
        request.app.state.dense_model,
        request.app.state.sparse_model,
        request.app.state.multi_model,
        request.app.state.vector_client)



async def init_vector_collection(client: AsyncQdrantClient, dense_size: int = VectorConfig.DENSE_MODEL_SIZE, multi_size: int = VectorConfig.MULTI_MODEL_SIZE):
    if not await client.collection_exists(VectorConfig.VECTOR_COLLECTION_NAME):
        await client.create_collection(collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
                                            vectors_config={
                                                "dense": models.VectorParams(
                                                    size=dense_size, 
                                                    distance=models.Distance.COSINE,
                                                    on_disk=True,
                                                    hnsw_config=models.HnswConfigDiff(
                                                        payload_m=16,
                                                        m=0,
                                                    )
                                                ),
                                                "multi": models.VectorParams(
                                                    size=multi_size,
                                                    distance=models.Distance.COSINE,
                                                    multivector_config=models.MultiVectorConfig(
                                                        comparator=models.MultiVectorComparator.MAX_SIM
                                                    ),
                                                    on_disk=True,
                                                    hnsw_config=models.HnswConfigDiff(m=0)
                                                ),
                                            },
                                            quantization_config= models.ScalarQuantization(
                                                scalar=models.ScalarQuantizationConfig(
                                                    type=models.ScalarType.INT8,
                                                    quantile=0.99,
                                                    always_ram=True,
                                                ),         
                                            ),
                                            sparse_vectors_config={
                                                "sparse": models.SparseVectorParams(
                                                    index=models.SparseIndexParams(on_disk=False)
                                                ),
                                            },
                                        )
        
        await client.create_payload_index(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            field_name="group_uid",
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=True,
            )
        )
        await client.create_payload_index(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            field_name="created_at",
            field_schema=models.PayloadSchemaType.DATETIME
        )

        await client.create_payload_index(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            field_name="user_uid",
            field_schema=models.PayloadSchemaType.UUID
        )

        await client.create_payload_index(
            collection_name=VectorConfig.VECTOR_COLLECTION_NAME,
            field_name="category_id",
            field_schema=models.PayloadSchemaType.INTEGER
        )
        