from dataclasses import dataclass
from typing import Any, TypeVar, Optional, Dict, Generic

from app.domain.exceptions.value_object import TaskResultException
from app.domain.value_objects.base import BaseValueObject

VT = TypeVar("VT", str, dict)

@dataclass(frozen=True)
class TaskResult(Generic[VT]):
    """
    Объект значения для результата выполнения задачи.
    Args:
        value (VT): Результат (может быть строкой или словарем).
    """
    value: VT = ""

    def validate(self) -> None:
        if not isinstance(self.value, (str, dict)):
            raise ValueError(f"Невалидный результат задачи: {self.value}")

    def as_generic_type(self) -> VT | str:
            if self.value is not None:
                return self.value
            else:
                return ""