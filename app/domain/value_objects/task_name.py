from dataclasses import dataclass

from app.domain.exceptions.value_object import TaskNameException
from app.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TaskName(BaseValueObject[str]):
    """
    Объект значения для имени задачи.
    Args:
        value (str): Название задачи.
    """
    value: str

    def validate(self)->None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise TaskNameException(message=f"Невалидное имя задачи: {self.value}")

    def as_generic_type(self) -> str:
        return self.value