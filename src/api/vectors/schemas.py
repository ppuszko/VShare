from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
class QueryFilters(BaseModel):
    created_at: datetime | None = None
    category_id: int | None = None # TODO: implement categories with redis etc.
    user_uid: UUID | None = None 