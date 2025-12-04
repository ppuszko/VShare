from pydantic import BaseModel
from src.core.db.models import Tier
from src.core.config import Config


class GroupCreate(BaseModel):
    name: str
    member_limit: int
    picture_storage: str = Config.DEFAULT_PICTURE


class GroupGet(BaseModel):
    name: str
    member_limit: int 
    member_count: int 
    picture_storage: str
    tier: Tier

    model_config = {
        "extra": "ignore"
    }