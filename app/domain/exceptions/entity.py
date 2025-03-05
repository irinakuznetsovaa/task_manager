from dataclasses import dataclass

from app.domain.exceptions.base import DomainException

@dataclass(frozen=True)
class EntityException(DomainException):
    message: str = "Entity error occurred."

    def __str__(self):
        return self.message

@dataclass(frozen=True)
class TaskError(EntityException):
    message: str = "Error related to the task."

    def __str__(self):
        return self.message
