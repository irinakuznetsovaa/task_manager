from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.entities.task import Task
from app.domain.exceptions.entity import TaskException, TaskNotFoundException
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass
class UpdateTaskUseCase:
    """
    Use case для обновления существующей задачи.
    """
    task_repository: TaskRepository

    async def execute(
        self,
        task_id: str,
        name: Optional[TaskName] = None,
        data: Optional[dict] = None,
    ) -> Task:
        """
        Обновляет информацию о задаче.
        Args:
            task_id (str): Идентификатор задачи.
            name (Optional[TaskName]): Новое имя задачи (если нужно изменить).
            data (Optional[dict]): Новые данные задачи.
        Return:
            Task: Обновленный объект задачи.
        Exception:
            TaskNotFoundException: Если задача с таким ID не найдена.
            TaskException: Если статус задачи не позволяет её обновление.
        """
        task = await self.task_repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundException(message=f"Задачи с таким ID - {task_id} не найдено.")

        if task.status!=TaskStatusEnum.PENDING:
            raise TaskTypeException(message=f"Обновление задачи с статусом - {task.status.value} невозможно")

        if name:
            task.update_name(TaskName(name).as_generic_type())
        if data:
            if data.task_type:
                new_task_data=FileTaskData(
                    task_type=TaskTypeEnum(data.task_type),
                    source_path=data.source_path,
                    destination_path=data.destination_path

                )
                task.update_task_data(new_task_data.as_generic_type())
        updated_task = await self.task_repository.update_task(task)
        return updated_task