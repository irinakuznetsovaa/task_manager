import os
import shutil
import time
from dataclasses import dataclass

from app.domain.exceptions.entity import TaskProcessingException
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_type import TaskTypeEnum
from pathlib import Path

@dataclass
class TaskProcessor:
    """
    Класс для обработки файловых задач: создания, копирования и удаления файлов.
    """
    async def _validate_path(self, path: str, must_exist: bool = False) -> None:
        """Валидация пути перед выполнением операции"""
        path_obj = Path(path)
        print(path_obj)
        print(path_obj.exists())
        print(os.access(path, os.W_OK))

        if must_exist and not path_obj.exists():
            raise FileNotFoundError(f"Файл {path} не найден")

        if must_exist and not os.access(path, os.R_OK):
            raise PermissionError(f"Нет прав на чтение файла {path}")

        if not must_exist and path_obj.exists() and not os.access(path, os.W_OK):
            raise PermissionError(f"Нет прав на запись в {path}")

    async def create_file(self, file: FileTaskData) -> None:
        try:
            await self._validate_path(file.source_path, must_exist=False)
            with open(file.source_path, 'w') as f:
                f.write('')
        except Exception as e:
            raise TaskProcessingException(f"Ошибка при создании файла {file.source_path}: {str(e)}")


    async def copy_file(self, file: FileTaskData) -> None:
        """Копирование файла"""
        try:
            await self._validate_path(file.source_path, must_exist=True)
            await self._validate_path(file.destination_path, must_exist=False)
            shutil.copy(file.source_path, file.destination_path)
        except Exception as e:
            raise TaskProcessingException(
                f"Ошибка при копировании файла {file.source_path} -> {file.destination_path}: {str(e)}")


    async def delete_file(self, file: FileTaskData) -> None:
        try:
            await self._validate_path(file.source_path, must_exist=True)
            os.remove(file.source_path)
        except Exception as e:
            raise TaskProcessingException(f"Ошибка при удалении файла {file.source_path}: {str(e)}")

    async def process(self, task_data: FileTaskData):
        """Общий метод обработки задач"""
        task_handlers = {
            TaskTypeEnum.FILE_CREATE.value: self.create_file,
            TaskTypeEnum.FILE_COPY.value: self.copy_file,
            TaskTypeEnum.FILE_DELETE.value: self.delete_file,
        }

        handler = task_handlers.get(task_data.task_type)
        if handler:
            await handler(task_data)
        else:
            raise TaskTypeException(f"Неподдерживаемый тип задачи: {task_data.task_type}")
