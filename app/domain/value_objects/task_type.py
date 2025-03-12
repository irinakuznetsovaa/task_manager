from enum import Enum

class TaskTypeEnum(str, Enum):
    FILE_CREATE = "FILE_CREATE"
    FILE_COPY = "FILE_COPY"
    FILE_DELETE = "FILE_DELETE"

