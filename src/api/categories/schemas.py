from pydantic import BaseModel


class CategoryGet(BaseModel):
    name: str
    id: int


class CategoryUpdate(BaseModel):
    new_name: str
    id: int