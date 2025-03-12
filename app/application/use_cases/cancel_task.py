from dataclasses import dataclass

from app.domain.exceptions.entity import TaskException, TaskNotFoundException
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from app.domain.repositories.task_repository import TaskRepository


@dataclass
class CancelTaskUseCase:
    """
    Use case для отмены задачи.
    """
    task_repository: TaskRepository
    async def execute(self, task_id: str) -> None:
        """
        Отменяет задачу, если она находится в статусе 'PENDING'.
        Args:
            task_id (str): Идентификатор задачи.
        Return:
            dict: Обновленные данные задачи (ID, статус, время обновления).
        Exception:
            TaskNotFoundException: Если задача с указанным ID не найдена.
            TaskTypeException: Если статус задачи не позволяет отмену.
        """
        task = await self.task_repository.get_task_by_id(task_id)
        if task:
            if task.status != TaskStatusEnum.PENDING:
                raise TaskTypeException(message=f"Отмена задачи с статусом - {task.status.value} невозможна")
            task.update_status(TaskStatus(TaskStatusEnum.CANCELED).as_generic_type())
            new_task=await self.task_repository.update_task(task)
            return {
                "id": new_task.id,
                "status": new_task.status,
                "updated_at": new_task.updated_at
            }
        else:
            raise TaskNotFoundException(message=f"Задачи с таким ID - {task_id} не найдено.")
