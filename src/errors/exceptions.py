from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, detail = "An error occured while processing request.", 
                 status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, headers = None):
        super().__init__(status_code, detail, headers)

class NotFoundError(AppError):
    def __init__(self, detail="Resource not found", headers=None):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND, headers=headers)

class ForbiddenError(AppError):
    def __init__(self, detail="Action not allowed!", headers=None):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN, headers=headers)

class NotVerifiedError(AppError): 
    def __init__(self, detail="You need to verify your account in order to perform this action", headers=None):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN, headers=headers)

class TokenInvalidError(AppError):
    def __init__(self, detail="This token is invalid. Log in to obtain new token", headers=None):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED, headers=headers)