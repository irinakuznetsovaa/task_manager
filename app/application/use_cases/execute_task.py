from dataclasses import dataclass
from typing import Any, Optional

from app.application.services.task_processor import TaskProcessor
from app.domain.entities.task import Task
from app.domain.exceptions.entity import TaskException, TaskNotFoundException, TaskAlreadyRunningException, \
    TaskProcessingException
from app.domain.exceptions.value_object import TaskTypeException, ValidationException, TaskStatusException
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatusEnum, TaskStatus
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass
class ExecuteTaskUseCase:
    """
    Use case для выполнения задачи.
    """
    task_repository: TaskRepository
    task_processor: TaskProcessor

    async def execute(
        self,
        task_id: str,
        is_retry:bool = False,
        is_celery:bool = False,
        is_last_attempt: bool = False,
    )->Task:
        """
        Запускает выполнение задачи.
        Args:
            task_id (str): Идентификатор задачи.
            is_retry (bool): Флаг повторного выполнения.
            is_celery (bool): Флаг использования Celery.
            is_last_attempt (bool): Флаг последней попытки.
        Return:
            Task: Обновленный объект задачи.
        Exception:
            TaskNotFoundException: Если задача не найдена.
            TaskStatusException: Если задача уже завершена.
            TaskAlreadyRunningException: Если задача уже выполняется.
            ValidationException: Если формат данных задачи некорректен.
            TaskProcessingException: Ошибка при выполнении задачи.
        """

        task=await self.task_repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundException(message=f"Задачи с таким ID - {task_id} не найдено.")

        if task.status in {TaskStatusEnum.COMPLETED, TaskStatusEnum.FAILED, TaskStatusEnum.CANCELED}:
            raise TaskStatusException(f"Запуск задачи {task_id} c статусом {task.status.value} невозможен.")

        if task.status == TaskStatusEnum.IN_PROGRESS and not is_retry:
            if is_celery:
                return task
            else:
                raise TaskAlreadyRunningException(f"Задача {task_id} уже выполняется!")

        task_data=task.task_data
        if not isinstance(task_data, dict) or "task_type" not in task_data:
            raise ValidationException(f"Некорректный формат данных: {task_data}")

        task_handlers = {
            TaskTypeEnum.FILE_CREATE.value: self.task_processor.create_file,
            TaskTypeEnum.FILE_COPY.value: self.task_processor.copy_file,
            TaskTypeEnum.FILE_DELETE.value: self.task_processor.delete_file,
        }

        if not is_retry:
            await self._set_status(task, TaskStatusEnum.IN_PROGRESS)

        try:
            task_type = TaskTypeEnum(task_data["task_type"]).value  # Переводим в Enum
            handler = task_handlers.get(task_type)
            await handler(FileTaskData(
                    task_type=TaskTypeEnum(task_data["task_type"]),
                    source_path=task_data["source_path"],
                    destination_path=task_data["destination_path"]

            ))
            await self._set_status(task, TaskStatusEnum.COMPLETED, "Задача выполнена успешно")
        except Exception as e:
            error_message = f"Ошибка выполнения задачи {task_id}: {str(e)}"

            if is_celery and not is_last_attempt:
                raise TaskProcessingException(error_message)

            await self._set_status(task, TaskStatusEnum.FAILED, error_message)
            raise TaskProcessingException(error_message)

        return task

    async def _set_status(self, task: Task, status: TaskStatusEnum, message: Optional[str] = None) -> None:
        task.update_status(status)
        if message:
            task.update_result(TaskResult(message).as_generic_type())
        await self.task_repository.update_task(task)







