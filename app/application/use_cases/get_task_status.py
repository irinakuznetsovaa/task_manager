from dataclasses import dataclass
from typing import Optional

from app.domain.entities.task import Task
from app.domain.exceptions.entity import TaskException, TaskNotFoundException
from app.domain.repositories.task_repository import TaskRepository


@dataclass(frozen=True)
class GetTaskStatusUseCase:
    """
    Use case для получения статуса конкретной задачи.
    """
    task_repository: TaskRepository

    async def execute(self, task_id: str) ->str:
        """
        Получает статус задачи по её идентификатору.
        Args:
            task_id (str): Идентификатор задачи.
        Return:
            dict: Данные о статусе задачи (ID, статус, результат, время обновления).
        Exception:
            TaskNotFoundException: Если задача с таким ID не найдена.
        """
        task:Optional[Task] = await self.task_repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundException(message=f"Задачи с таким ID - {task_id} не найдено.")
        return {
            "id": task.id,
            "status": task.status,
            "result": task.result,
            "updated_at": task.updated_at
        }

