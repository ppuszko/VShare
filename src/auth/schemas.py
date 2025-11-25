from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from src.db.models import UserRole


class UserCreate(BaseModel):
    username: str = Field(max_length=20, min_length=4)
    email: str
    password: str = Field(min_length=8, max_length=40)
    role: UserRole = UserRole.USER 


class UserLogin(BaseModel):
    email: str
    password: str

