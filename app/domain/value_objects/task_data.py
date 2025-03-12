from abc import ABC
from dataclasses import dataclass

from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.base import BaseValueObject
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass(frozen=True)
class TaskData(ABC):
    """
    Абстрактный класс для данных задачи.
    Args:
        task_type (TaskTypeEnum): Тип задачи.
    """
    task_type: TaskTypeEnum

    def __post_init__(self):
        self.validate()

    def validate(self)->None:
        if not isinstance(self.task_type, TaskTypeEnum):
            raise TaskTypeException(message=f"Невалидный TaskType: {self.task_type}")

    def as_generic_type(self)-> dict:
        return {"task_type": self.task_type.value}