from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.types import UserDefinedType

class Document(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path_to_doc: str
    owner_id: int
    chunks: list["Chunk"] = Relationship(back_populates="document")



class Chunk(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chunk_text: str
    doc_id: int = Field(foreign_key="document.id")

    document: "Document" | None = Relationship(back_populates="chunks")

    embedding: "Embedding"| None = Relationship(back_populates="chunk")

class Vector(UserDefinedType):
    def get_col_spec(self, **kw):
        return "vector(384)"

class Embedding(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chunk_id: int = Field(foreign_key="chunk.id")
    embedding_vector: list[float] = Field(sa_column=Column(Vector))

    chunk: "Chunk" | None = Relationship(back_populates="embedding")