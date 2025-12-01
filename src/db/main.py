from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from collections.abc import AsyncGenerator


def init_engine(url: str) -> AsyncEngine:
    return create_async_engine(url=url)

def init_sesssionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.sessionmaker() as session:
        yield session

