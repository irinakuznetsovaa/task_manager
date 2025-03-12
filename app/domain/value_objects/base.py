from abc import ABC,abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

VT=TypeVar('VT', bound=Any)
@dataclass(frozen=True)
class BaseValueObject(ABC,Generic[VT]):
    """
    Базовый класс для  Value Object.
    Args:value (VT): Хранимое значение.
    """
    value: VT

    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self)->None:
        pass

    @abstractmethod
    def as_generic_type(self)->VT:
        pass