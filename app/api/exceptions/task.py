from fastapi import HTTPException, status
from dataclasses import dataclass

@dataclass
class CustomHTTPException(HTTPException):
    status_code: int
    detail: str

    def __post_init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

@dataclass
class ConflictException(CustomHTTPException):
    detail: str = "Конфликт запроса"
    status_code: int = status.HTTP_409_CONFLICT


@dataclass
class BadRequestException(CustomHTTPException):
    status_code :int = status.HTTP_400_BAD_REQUEST
    detail: str = "Некорректный запрос"

@dataclass
class NotFoundException(CustomHTTPException):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "Данные не найдены"

@dataclass
class InternalServerException(CustomHTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Внутренняя ошибка сервера"

