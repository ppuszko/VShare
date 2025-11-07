from sqlmodel import SQLModel, Field, Relationship, Enum as PgEnum
from sqlalchemy import Column, func, DateTime
from sqlalchemy.types import UserDefinedType
import uuid
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    path_to_document: str = Field(nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="users.uid")
    is_public: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    ))
    updated_at: datetime = Field(sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    ))

    embeddings: list["Embedding"] = Relationship(back_populates="document", sa_relationship_kwargs={'lazy':'selectin'})
    owner: "User" = Relationship(back_populates="document")

    def __repr__(self):
        return f"<Document uid: {self.uid} by {self.owner_id}"


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(exclude=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    ))
    updated_at: datetime = Field(sa_column=Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    ))
    role: UserRole = Field(sa_column=Column(
        PgEnum(UserRole, name="user_role"),
        nullable=False,
        server_default=UserRole.USER
    ))

    documents: list["Document"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy':'selectin'})


    def __repr__(self):
        return f"<User {self.username}>"

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
    __tablename__ = "embeddings"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_uid: uuid.UUID = Field(foreign_key="documents.uid")
    embedding_vector: list[float] = Field(sa_column=Column(Vector))
    chunk_str: str = Field(nullable=False)


    document: "Document" = Relationship(back_populates="embedding")