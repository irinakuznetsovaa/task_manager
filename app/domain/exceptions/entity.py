from dataclasses import dataclass

from app.domain.exceptions.base import DomainException

@dataclass
class EntityException(DomainException):
    """ Исключение, связанное с ошибками сущностей."""
    message: str = "Ошибка entity."


@dataclass
class TaskException(EntityException):
    """ Ошибка, связанная с задачами."""
    message: str = "Ошибка задачи"

@dataclass
class TaskNotFoundException(TaskException):
    """ Исключение, возникающее, если задача не найдена. """
    message:str = "Задача не найдена"

@dataclass
class TaskProcessingException(TaskException):
    """Исключение, возникающее при ошибках обработки задач."""
    message:str = "Ошибка обработки задачи"

@dataclass
class TaskAlreadyRunningException(TaskException):
    """ Исключение, возникающее, если задача уже выполняется. """
    message:str ="Задача уже выполняется"
