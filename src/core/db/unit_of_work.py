from fastapi.requests import Request
from sqlmodel.ext.asyncio.session import AsyncSession


class UnitOfWork:
    def __init__(self, sessionmaker):
        self._sessionmaker = sessionmaker
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._sessionmaker()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_val:
                await self._session.rollback()
            else:
                await self._session.commit()

            await self._session.close()
            self._session = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise Exception("Session not initialized. UnitOfWork was used out of it's context.")
        return self._session

async def get_uow(request: Request) -> UnitOfWork:
    return UnitOfWork(request.app.state.sessionmaker)