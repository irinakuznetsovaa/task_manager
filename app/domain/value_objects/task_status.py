from dataclasses import dataclass

from app.domain.exceptions.value_object import TaskStatusException
from app.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TaskStatus(BaseValueObject):
    value: str
    VALID_STATUSES = {"PENDING", "PROCESSING", "COMPLETED", "FAILED","CANCELED"}

    def validate(self):
        if self.value not in self.VALID_STATUSES:
            raise TaskStatusException(message=f"Invalid status: {self.value}")

    def as_generic_type(self):
        return self.value