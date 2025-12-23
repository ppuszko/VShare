from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from fastembed import SparseTextEmbedding, LateInteractionTextEmbedding
from sentence_transformers import SentenceTransformer

from src.api.vectors.main import(
    load_dense_model, 
    load_multivector_model, 
    load_sparse_model
)

    
    

class QueryFilters(BaseModel):
    created_at: datetime | None = None
    category_id: int | None = None # TODO: implement categories with redis etc.
    user_uid: UUID | None = None 


class DocumentAdd(BaseModel):
    group_uid: UUID | None = None 
    user_uid: UUID | None = None
    storage_path: str | None = None
    title: str 
    category_id: int 

class DocumentGet(BaseModel):
    id: int
    group_uid: UUID
    user_uid: UUID
    title: str 
    category_id: int | None


class EmbModels:
    def __init__(self):
        self.dense_model: SentenceTransformer = load_dense_model()
        self.sparse_model: SparseTextEmbedding  = load_sparse_model()
        self.multi_model: LateInteractionTextEmbedding = load_multivector_model()