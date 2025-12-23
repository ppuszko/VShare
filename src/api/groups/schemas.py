from pydantic import BaseModel
from uuid import UUID

from src.core.db.models import Tier
from src.core.config.file import FileConfig


class GroupCreate(BaseModel):
    name: str
    tier: Tier
    picture_storage: str = FileConfig.DEFAULT_PICTURE_PATH
    member_limit: int = 20


class GroupGet(BaseModel):
    uid: UUID
    name: str
    member_limit: int 
    member_count: int 
    picture_storage: str
    tier: Tier

    model_config = {
        "extra": "ignore"
    }