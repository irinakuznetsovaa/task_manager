from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class DomainException(Exception):
    message: str = "Application error occurred"

    def __str__(self):
        return self.message
