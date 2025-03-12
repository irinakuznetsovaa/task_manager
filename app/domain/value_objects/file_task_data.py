import os
from dataclasses import dataclass
from typing import Optional

from app.domain.exceptions.value_object import PathEmptyException, ForbiddenCharacterException, InvalidPathException
from app.domain.value_objects.base import BaseValueObject
from app.domain.value_objects.task_data import TaskData
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass(frozen=True)
class FileTaskData(TaskData):
    """
    Объект значения для данных задачи, связанной с файловыми операциями.
    Args:
        source_path (str): Исходный путь к файлу.
        destination_path (Optional[str]): Путь назначения.
    """
    source_path: str
    destination_path: Optional[str] = None


    def validate(self) -> None:
        super().validate()
        # Проверка на пустой путь
        if not self.source_path:
            raise PathEmptyException(message="Source path не может быть пустым")

        # Проверка на наличие запрещенных символов в пути
        forbidden_chars = ['<', '>', '"', '|', '?', '*']
        if any(char in self.source_path for char in forbidden_chars):
            raise ForbiddenCharacterException(message=f"Source path не должен содержать запрещенных символов: {', '.join(forbidden_chars)}")
        normalized_source_path = os.path.abspath(self.source_path)
        if not os.path.isabs(normalized_source_path):
            raise InvalidPathException("Source path - путь должен быть абсолютным")
        if self.task_type == TaskTypeEnum.FILE_COPY and not self.destination_path:
            raise PathEmptyException(message="Destination path не может быть пустым для операции копирования")
        # Валидация для destination_path
        if self.destination_path:
            # Проверка на наличие запрещенных символов в destination_path
            if any(char in self.destination_path for char in forbidden_chars):
                raise ForbiddenCharacterException(message=f"Destination path не должен содержать запрещенных символов: {', '.join(forbidden_chars)}")
            normalized_destination_path = os.path.abspath(self.destination_path)
            if not os.path.isabs(normalized_destination_path):
                raise InvalidPathException("Destination path - путь должен быть абсолютным")


    def as_generic_type(self) -> dict:
        base_data = super().as_generic_type()
        base_data.update({
            "source_path": self.source_path,
            "destination_path": self.destination_path
        })
        return base_data
