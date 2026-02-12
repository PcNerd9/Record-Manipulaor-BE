from fastapi import HTTPException, status
from typing import Any

class APIException(HTTPException):
    def __init__(self, status_code: int, message: str, data: dict[str, Any] | None = None):
        
        data_dict: dict[str, Any] = {
            "status_code": status_code,
            "status": "error",
            "message": message
        }
        if data:
            data_dict["data"] = data
        
        super().__init__(status_code=status_code, detail=data_dict)
        

class BadRequestException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message, data=data)
        
class UnauthorizedException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message, data=data)
        
class ForbiddenException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message, data=data)
        
class NotFoundException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, data=data)
        
class ConflictException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message, data=data)
        
class GoneException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_410_GONE, message=message, data=data)
        
class InternalServerException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message, data=data)
        
        
class UnprocessableEntityException(APIException):
    def __init__(self, message: str, data: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, message=message, data=data)