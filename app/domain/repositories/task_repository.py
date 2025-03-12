from dataclasses import dataclass
from abc import ABC,abstractmethod
from datetime import datetime
from typing import Optional, List

from app.domain.entities.task import Task
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass
class TaskRepository(ABC):
    """
       Абстрактный класс, определяющий интерфейс для работы с хранилищем задач.
    """
    @abstractmethod
    async def create_task(self,task:Task) -> Task:
        """
        Создает новую задачу в хранилище.
        Args:task (Task): Объект задачи.
        Returns: Task: Созданная задача.
        """
        pass

    @abstractmethod
    async def get_task_by_id(self, task_id:str)->Optional[Task]:
        """
        Получает задачу по идентификатору.
        Args:task_id (str): Идентификатор задачи.
        Returns:Optional[Task]: Найденная задача или None, если не найдена.
        """
        pass

    @abstractmethod
    async def get_tasks(
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
        Получает список задач с возможностью фильтрации.
        Args:
            name (Optional[TaskName]): Фильтр по имени.
            created_at_from (Optional[datetime]): Фильтр по дате создания (от).
            created_at_to (Optional[datetime]): Фильтр по дате создания (до).
            updated_at_from (Optional[datetime]): Фильтр по дате обновления (от).
            updated_at_to (Optional[datetime]): Фильтр по дате обновления (до).
            status (Optional[TaskStatusEnum]): Фильтр по статусу задачи.
            task_type (Optional[TaskTypeEnum]): Фильтр по типу задачи.
        Returns:List[Task]: Список найденных задач.
        """
        pass

    @abstractmethod
    async def update_task(self,task: Task) -> Task:
        """
        Обновляет существующую задачу.
        Args:task (Task): Обновленные данные задачи.
        Returns:Task: Обновленная задача.
        """
        pass

    @abstractmethod
    async def delete_task(self,task_id:str)->None:
        """
        Удаляет задачу по идентификатору.
        Args:task_id (str): Идентификатор задачи.
        """
        pass