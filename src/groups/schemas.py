from pydantic import BaseModel
from src.db.models import Tier

class GroupCreate(BaseModel):
    name: str
    member_limit: int
    picture_storage: str


class GroupGet(BaseModel):
    name: str
    member_limit: int 
    member_count: int 
    picture_storage: str
    tier: Tier

    model_config = {
        "extra": "ignore"
    }