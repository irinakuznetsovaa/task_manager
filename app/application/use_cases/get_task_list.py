from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from app.domain.entities.task import Task
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum
from app.domain.repositories.task_repository import TaskRepository


@dataclass(frozen=True)
class GetTaskListUseCase:
    """
    Use case для получения списка задач с возможностью фильтрации.
    """
    task_repository: TaskRepository

    async def execute(
        self,
        name: Optional[TaskName] = None,
        created_at_from:Optional[datetime]=None,
        created_at_to:Optional[datetime]=None,
        updated_at_from: Optional[datetime] = None,
        updated_at_to: Optional[datetime] = None,
        status: Optional[TaskStatusEnum] = None,
        task_type: Optional[TaskTypeEnum] = None
    ) -> List[Task]:
        """
        Получает список задач с возможными фильтрами.

        Args:
            name (Optional[TaskName]): Фильтр по имени задачи.
            created_at_from (Optional[datetime]): Фильтр по дате создания (от).
            created_at_to (Optional[datetime]): Фильтр по дате создания (до).
            updated_at_from (Optional[datetime]): Фильтр по дате обновления (от).
            updated_at_to (Optional[datetime]): Фильтр по дате обновления (до).
            status (Optional[TaskStatusEnum]): Фильтр по статусу задачи.
            task_type (Optional[TaskTypeEnum]): Фильтр по типу задачи.

        Return:
            List[Task]: Список найденных задач.
        """
        return await self.task_repository.get_tasks(
            name=name,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            updated_at_from=updated_at_from,
            updated_at_to=updated_at_to,
            status=status,
            task_type=task_type
        )

