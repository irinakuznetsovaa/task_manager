from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime

from app.domain.exceptions.value_object import ValidationException
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_data import TaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum


@dataclass
class Task:
    """
    Класс, представляющий задачу.

    Атрибуты:
        name (TaskName): Название задачи.
        task_data (TaskData): Данные задачи.
        status (TaskStatus): Текущий статус задачи (по умолчанию PENDING).
        result (TaskResult): Результат выполнения задачи.
        created_at (datetime): Дата и время создания задачи.
        updated_at (datetime): Дата и время последнего обновления задачи.
        id (str): Уникальный идентификатор задачи (UUID).
    """
    name: TaskName
    task_data:TaskData
    status: TaskStatus = field(default_factory=lambda: TaskStatus(TaskStatusEnum.PENDING),kw_only=True)
    result: TaskResult = field(default_factory=lambda: TaskResult(''),kw_only=True)
    created_at: datetime = field(default_factory=datetime.utcnow,kw_only=True)
    updated_at: datetime = field(default_factory=datetime.utcnow,kw_only=True)
    id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)

    def update_status(self, new_status: TaskStatus)->None:
        """
        Обновляет статус задачи.
        Args:new_status (TaskStatus): Новый статус задачи.
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update_result(self, new_result: TaskResult)->None:
        """
        Обновляет результат выполнения задачи.
        Args:new_result (TaskResult): Новый результат.
        """
        self.result = new_result
        self.updated_at = datetime.utcnow()

    def update_name(self, new_name: TaskName)->None :
        """
        Обновляет название задачи.
        Args:new_name (TaskName): Новое имя задачи.
        """
        self.name = new_name
        self.updated_at = datetime.utcnow()

    def update_task_data(self,task_data: TaskData)->None:
        """
        Обновляет данные задачи.
        Args:task_data (TaskData): Новые данные задачи.
        """
        self.task_data = task_data
        self.updated_at = datetime.utcnow()
