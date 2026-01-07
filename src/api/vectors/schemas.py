from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class QueryFilters(BaseModel):
    group_uid: UUID | None = None
    time_frame: tuple[datetime | None, datetime | None] = (None, None)
    category_id: list[int] | None = None
    user_uid: UUID | None = None 
    only_my_articles: bool = False


