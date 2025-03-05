from dataclasses import dataclass

from app.domain.exceptions.base import DomainException


@dataclass(frozen=True, eq=False)
class ValidationException(DomainException):
    message: str = "Validation error occurred."

    def __str__(self):
        return self.message


@dataclass(frozen=True)
class TaskStatusException(ValidationException):
    message: str = "Invalid task status."

    def __str__(self):
        return self.message


@dataclass(frozen=True)
class FileSizeException(ValidationException):
    message: str = "File size exceeds the limit."

    def __str__(self):
        return self.message


@dataclass(frozen=True)
class FilePathException(ValidationException):
    message: str = "Invalid file path."

    def __str__(self):
        return self.message