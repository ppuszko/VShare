import functools
from fastapi import HTTPException, status
from .exceptions import AppError

def handle_exceptions(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"While processing request an exception occured. Exception: {e}\n")
    return wrapper