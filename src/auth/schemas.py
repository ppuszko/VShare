from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from src.db.models import UserRole
from src.groups.schemas import GroupGet
import uuid 

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
    username: str
    email: str
    group: GroupGet | None

