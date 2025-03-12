from dataclasses import dataclass
from enum import Enum

from app.domain.exceptions.value_object import TaskStatusException
from app.domain.value_objects.base import BaseValueObject

class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

@dataclass(frozen=True)
class TaskStatus(BaseValueObject[TaskStatusEnum]):
    """
    Объект значения для статуса задачи.
    Args:
        value (TaskStatusEnum): Текущий статус задачи.
    """
    value: TaskStatusEnum

    def validate(self):
        if not isinstance(self.value, TaskStatusEnum):
            raise TaskStatusException(message=f"Невалидный статус задачи: {self.value}")

    def as_generic_type(self) -> TaskStatusEnum:
        return self.value