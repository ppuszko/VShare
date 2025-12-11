from qdrant_client import models, AsyncQdrantClient
from src.core.config import Config
from fastapi import Request, Depends

def init_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=Config.VECTOR_DB_URL)

async def get_vector_client(request: Request) -> AsyncQdrantClient:
    return request.app.state.vector_client


async def init_collection(dense_size: int, multi_size: int, client: AsyncQdrantClient = Depends(get_vector_client)):
    if not await client.collection_exists(Config.VECTOR_COLLECTION_NAME):
        await client.create_collection(collection_name=Config.VECTOR_COLLECTION_NAME,
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
            collection_name=Config.VECTOR_COLLECTION_NAME,
            field_name="group_uid",
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=True,
            )
        )
        await client.create_payload_index(
            collection_name=Config.VECTOR_COLLECTION_NAME,
            field_name="created_at",
            field_schema=models.PayloadSchemaType.DATETIME
        )

        await client.create_payload_index(
            collection_name=Config.VECTOR_COLLECTION_NAME,
            field_name="user_uid",
            field_schema=models.PayloadSchemaType.UUID
        )


        # TODO: measure the time needed to fully process and insert single 20 page document. If it is above 3 seconds, consider Celery, else use asyncio
        # TODO: implement per-tenant categories table and caching for it 
        # TODO: implement vector worker class for chunking, creating embeddings and interacting with qdrant.