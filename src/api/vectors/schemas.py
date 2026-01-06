from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class QueryFilters(BaseModel):
    group_uid: UUID | None = None
    time_frame: tuple[datetime | None, datetime | None] = (None, None)
    category_id: list[int] | None = None
    user_uid: UUID | None = None 
    only_my_articles: bool = False


class DocumentAdd(BaseModel):
    id: int | None = None
    group_uid: UUID | None = None 
    user_uid: UUID | None = None
    storage_path: str | None = None
    created_at: datetime | None = None
    title: str 
    category_id: int | None

