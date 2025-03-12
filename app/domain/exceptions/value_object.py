from dataclasses import dataclass

from app.domain.exceptions.base import DomainException


@dataclass
class ValidationException(DomainException):
    """ Исключение, возникающее если данные невалидны. """
    message: str = "Ошибка валидации."


@dataclass
class TaskStatusException(ValidationException):
    """ Исключение, возникающее если статус задачи невалиден. """
    message: str = "Невалидный статус задачи."


@dataclass
class TaskTypeException(ValidationException):
    """ Исключение, возникающее если тип задачи невалиден. """
    message: str = "Невалидный тип задачи."


@dataclass
class TaskNameException(ValidationException):
    """ Исключение, возникающее если имя задачи невалидно. """
    message: str = "Невалидное имя задачи."

@dataclass
class TaskResultException(ValidationException):
    """ Исключение, возникающее если результат задачи невалиден. """
    message: str = "Невалидный результат задачи."

@dataclass
class FileValidationException(ValidationException):
    """ Исключение, возникающее если файл невалиден. """
    message: str = "Невалидный file"

@dataclass
class PathEmptyException(FileValidationException):
    """ Исключение, возникающее путь к файлу пустой """
    message: str = "FileTaskData - путь не может быть пустым"

@dataclass
class ForbiddenCharacterException(FileValidationException):
    """ Исключение, возникающее есть путь содержит запрещенные символы """
    message: str = "FileTaskData - путь содержит запрещенные символы"


@dataclass
class InvalidPathException(FileValidationException):
    """ Исключение, возникающее есть путь не абсолютный """
    message: str = "FileTaskData - путь должен быть абсолютным"




