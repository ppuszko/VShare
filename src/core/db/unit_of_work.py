from fastapi.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession


class UnitOfWork:
    def __init__(self, sessionmaker):
        self._sessionmaker = sessionmaker
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self._sessionmaker()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.session.rollback() # type:ignore
        else:
            await self.session.commit() # type: ignore

        await self.session.close() # type: ignore
        self.session = None

    @property
    def get_session(self) -> AsyncSession:
        if self.session is None:
            raise Exception("Session not initialized. UnitOfWork was used out of it's context.")
        return self.session

async def get_uow(request: Request) -> UnitOfWork:
    return UnitOfWork(request.app.state.sessionmaker)