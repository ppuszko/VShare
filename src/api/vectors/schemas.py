from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class QueryFilters(BaseModel):
    created_at: datetime | None = None
    category_id: int | None = None # TODO: implement categories with redis etc.
    user_uid: UUID | None = None 


class DocumentAdd(BaseModel):
    group_uid: UUID
    user_uid: UUID
    storage_path: str
    title: str 
    category_id: int | None = None