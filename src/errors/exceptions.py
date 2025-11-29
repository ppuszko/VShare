from fastapi import HTTPException, status


class AppError(Exception):
    def __init__(self, detail = "An error occured while processing request.", 
                 status_code = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, detail="Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class ForbiddenError(AppError):
    def __init__(self, detail="Action not allowed!"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class NotVerifiedError(AppError): 
    def __init__(self, detail="You need to verify your account in order to perform this action"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class TokenInvalidError(AppError):
    def __init__(self, detail="This token is invalid. Log in to obtain new token"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class BadRequest(AppError):
    def __init__(self, detail="Bad request!"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)