import functools
from fastapi import HTTPException, status
from .exceptions import AppError
from src.core.config import Config

def handle_exceptions(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            raise
        except Exception as e:
            if Config.APP_ENV == "DEV":
                detail = f"Exception: {e}\n"
            else:
                detail = "Ooops, Something went wrong!"
            raise AppError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=detail)
    return wrapper