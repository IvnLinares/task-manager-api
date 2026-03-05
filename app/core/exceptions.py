from fastapi import HTTPException, status

class ErrorMessages:
    INVALID_CREDENTIALS = "Could not validate credentials"
    INCORRECT_LOGIN = "Incorrect email or password"
    INACTIVE_USER = "Inactive user"
    NOT_FOUND = "Resource not found"
    FORBIDDEN = "Not enough permissions"
    ALREADY_EXISTS = "Resource already exists"

def get_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorMessages.INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_incorrect_login_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorMessages.INCORRECT_LOGIN,
    )

def get_inactive_user_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorMessages.INACTIVE_USER,
    )

def get_forbidden_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=ErrorMessages.FORBIDDEN,
    )

def get_not_found_exception(detail: str = ErrorMessages.NOT_FOUND) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )
    
def get_already_exists_exception(detail: str = ErrorMessages.ALREADY_EXISTS) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )
