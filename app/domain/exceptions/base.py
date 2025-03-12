from dataclasses import dataclass


@dataclass
class DomainException(BaseException):
    """
    Базовое исключение для всех ошибок в доменном слое приложения.
    Args:message (str): Сообщение об ошибке.
    """
    message: str = "Произошла ошибка приложения"

    def __str__(self):
        return self.message
