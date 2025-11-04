from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.types import UserDefinedType

class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path_to_document: str
    owner_id: int
    is_public: bool

    embeddings: list["Embedding"] = Relationship(back_populates="document")


class Vector(UserDefinedType):
    def get_col_spec(self, **kw):
        return "vector(384)"
    
    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                return f"[{','.join(map(str, value))}]"
            return value
        return process
    
    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                value = value.strip("[]")
                return list(map(float, value.split(",")))
            return value
        return process

class Embedding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    embedding_vector: list[float] = Field(sa_column=Column(Vector))
    chunk_str: str


    document: "Document" | None = Relationship(back_populates="embedding")