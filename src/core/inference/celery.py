from typing import TYPE_CHECKING

from celery import Celery



app = Celery('VShare', 
             broker="redis://localhost", 
             include=["src.core.inference.tasks"],)


if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.models import SparseTextEmbedding, TextEmbedding, LateInteractionTextEmbedding
    from httpx import Client

dense_model: "TextEmbedding" = None # type: ignore
sparse_model: "SparseTextEmbedding" = None # type: ignore
multi_model: "LateInteractionTextEmbedding" = None # type: ignore

client: "QdrantClient" = None # type: ignore
http_client: "Client" = None # type: ignore


