from pydantic import BaseModel, Field

from datetime import datetime
from src.core.db.models import UserRole
from src.api.groups.schemas import GroupGet
from uuid import UUID 

class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    email: str
    password: str = Field(min_length=8, max_length=40)
    role: UserRole = UserRole.USER 
    group_uid: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str


class UserGet(BaseModel):
    uid: UUID
    username: str
    email: str
    role: UserRole
    group: GroupGet 

class UserInvite(BaseModel):
    email: str
    role: UserRole = UserRole.USER
    group_uid: str = ""    


class UserMissingCredentials(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=40)
