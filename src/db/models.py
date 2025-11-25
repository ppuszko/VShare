from sqlmodel import SQLModel, Field, Relationship, Enum as PgEnum
from sqlalchemy import Column, func, DateTime
import uuid
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    GROUP_ADMIN = "GROUP_ADMIN"
    USER = "USER"


class Group(SQLModel, table=True):
    __tablename__: str = "groups"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    member_limit: int = Field(nullable=False)
    member_count: int = Field(nullable=False, default=1)

    members: list["User"] = Relationship(back_populates="groups")

class User(SQLModel, table=True):
    __tablename__: str = "users"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(exclude=True)
    refresh_jti_hash: str = Field(exclude=True, nullable=False)
    is_verified: bool = Field(default=False)
    group_uid: uuid.UUID = Field(default = None, foreign_key="groups.uid")
    role: UserRole = Field(sa_column=Column(
        PgEnum(UserRole, name="user_role"),
        nullable=False,
        server_default=UserRole.USER
    ))
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

    group: Group = Relationship(back_populates="users", sa_relationship_kwargs={"lazy":"selectin"})
    


    def __repr__(self):
        return f"<User {self.username}>"

