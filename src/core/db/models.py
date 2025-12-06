from sqlmodel import SQLModel, Field, Relationship, Enum as PgEnum
from sqlalchemy import Column, func, DateTime
import uuid
from datetime import datetime
import enum
from src.core.config import Config


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    GROUP_ADMIN = "GROUP_ADMIN"
    USER = "USER"

class Tier(str, enum.Enum):
    MINI = "MINI"
    NORMAL = "NORMAL"
    LARGE = "LARGE"


class Group(SQLModel, table=True):
    __tablename__: str = "groups"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    member_limit: int = Field(nullable=False)
    member_count: int = Field(nullable=False, default=1)
    picture_storage: str = Field(nullable=False, default=f"{Config.PICTURE_STORAGE}/default.jpg")
    tier: Tier = Field(sa_column=Column(
        PgEnum(Tier, name="tier"),
        nullable=False,
        server_default=Tier.MINI
    ))

    members: list["User"] = Relationship(back_populates="group")

class User(SQLModel, table=True):
    __tablename__: str = "users"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    password_hash: str = Field(exclude=True)
    refresh_jwt_hash: str = Field(exclude=True, nullable=True)
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

    group: Group | None = Relationship(back_populates="members", sa_relationship_kwargs={"lazy":"selectin"})


    def __repr__(self):
        return f"<User {self.username}>"

