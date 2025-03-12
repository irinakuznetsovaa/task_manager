from dataclasses import dataclass
from typing import Optional

from app.domain.entities.task import Task
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass
class CreateTaskUseCase:
    """
    Use case для создания новой задачи.
    """
    task_repository: TaskRepository

    async def execute(
        self,
        name: str,
        data: dict,
    )->Task:
        """
        Создает новую задачу.
        Args:
            name (str): Название задачи.
            data (dict): Данные задачи .

        Return:
            Task: Созданная задача.

        Exception:
            TaskTypeException: Если передан неподдерживаемый тип задачи.
        """
        task_name = TaskName(name)

        try:
            task_type_enum=TaskTypeEnum(data.get("task_type"))
        except ValueError:
            raise TaskTypeException(message=f"Неподдерживаемый тип задачи: {data.get('task_type')}")

        if task_type_enum in [TaskTypeEnum.FILE_CREATE, TaskTypeEnum.FILE_COPY, TaskTypeEnum.FILE_DELETE]:
            task_data=FileTaskData(
                task_type=task_type_enum,
                source_path=data.get("source_path"),
                destination_path=data.get("destination_path")
            )
        else:
            raise TaskTypeException(message=f"Неподдерживаемый тип задачи: {task_type_enum}")

        task=Task(
            name=task_name,
            task_data=task_data,
            status=TaskStatus(TaskStatusEnum.PENDING),
            result=TaskResult(None)
        )
        return await self.task_repository.create_task(task)
