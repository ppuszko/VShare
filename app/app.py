from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import create_engine, Session, SQLModel
import static_details


connection_string = static_details.DB_CONNECTION_STRING
connect_args = {"check_same_thread": False}
engine = create_engine(connection_string, connect_args=connect_args)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)