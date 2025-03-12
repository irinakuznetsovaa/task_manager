import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime

from pydantic_core.core_schema import ValidationInfo

from app.api.exceptions.task import BadRequestException
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum


class FileTaskData(BaseModel):
    task_type: TaskTypeEnum = Field(
        ...,
        title="Тип задачи",
        description="Тип выполняемой задачи: создание файла(FILE_CREATE), копирование файла(FILE_COPY) и удаление файла(FILE_DELETE)",
        example="FILE_CREATE"
    )
    source_path: str = Field(
        ...,
        title='Исходный путь файла',
        description="Исходный путь файла",
        example="/app/files/file.txt"
    )
    destination_path: Optional[None|str] = Field(
        None,
        title='Целевой путь файла',
        description="Целевой путь для копирования",
        example=""
    )
class CreateTaskRequest(BaseModel):
    name:str = Field(
        ...,
        min_length=1,
        title='Наименование задачи',
        description="Наименование задачи",
        example='Task'
    )
    task_data: FileTaskData


class CreateTaskResponse(BaseModel):
    id: str = Field(
        ...,
        title="Идентификатор задачи",
        description="Уникальный идентификатор задачи в формате uuid",
    )
    name: str = Field(
        ...,
        min_length=1,
        title='Наименование задачи',
        description="Наименование задачи",
        example='Task'
    )
    task_data: FileTaskData
    status: str = Field(
        ...,
        title='Статус задачи',
        description="Статус задачи - 'PENDING','IN_PROGRESS','COMPLETED','FAILED','CANCELED'"
    )
    result: Optional[str] = Field(
        None,
        title='Результат выполнения задачи',
        description='Содержит результат выполнения задачи или возникшие ошибки в ходе выполнения '
    )
    created_at: datetime = Field(
        ...,
        title='Дата и время создания задачи',
        description='Дата и время создания задачи'
    )
    updated_at: datetime = Field(
        ...,
        title='Дата и время обновления задачи',
        description='Дата и время обновления задачи'
    )
    model_config = ConfigDict(from_attributes=True)




class GetStateTaskResponse(BaseModel):
    id:str = Field(
        ...,
        title="Идентификатор задачи",
        description="Уникальный идентификатор задачи в формате uuid",
    )
    status:TaskStatusEnum = Field(
        ...,
        title='Статус задачи',
        description="Статус задачи"
    )
    result: Optional[str] = Field(
        None,
        title='Результат выполнения задачи',
        description='Содержит результат выполнения задачи или возникшие ошибки в ходе выполнения '
    )
    updated_at: datetime = Field(
        ...,
        title='Дата и время обновления задачи',
        description='Дата и время обновления задачи'
    )
    model_config = ConfigDict(from_attributes=True)


class GetTaskListRequest(BaseModel):
    name: Optional[str] = Field(
        None,
        title="Название задачи",
        description="Фильтр по названию"
    )
    status: Optional[TaskStatusEnum] = Field(
        None,
        title="Статус",
        description="Фильтр по статусу задачи"
    )
    task_type: Optional[TaskTypeEnum] = Field(
        None,
        title="Тип задачи",
        description="Фильтр по типу задачи"
    )
    created_at_from: Optional[datetime] = Field(
        None, title="Создано с",
        description="Фильтр по дате создания (с какого момента)"
    )
    created_at_to: Optional[datetime] = Field(
        None, title="Создано до",
        description="Фильтр по дате создания (до какого момента)"
    )
    updated_at_from: Optional[datetime] = Field(
        None, title="Создано с",
        description="Фильтр по дате обновления (с какого момента)"
    )
    updated_at_to: Optional[datetime] = Field(
        None, title="Создано до",
        description="Фильтр по дате обновления (до какого момента)"
    )
    @model_validator(mode="after")
    def validate_dates(self):
        if self.created_at_from and self.created_at_to and self.created_at_from > self.created_at_to:
            raise BadRequestException(detail="created_at_from не может быть больше created_at_to")
        if self.updated_at_from and self.updated_at_to and self.updated_at_from > self.updated_at_to:
            raise BadRequestException(detail="updated_at_from не может быть больше updated_at_to")
        if self.created_at_from and self.updated_at_to and self.created_at_from > self.updated_at_to:
            raise BadRequestException(detail="created_at_from не может быть больше updated_at_to")
        return self

class FileTaskDataUpdate(BaseModel):
    task_type: TaskTypeEnum = Field(
        ...,
        title="Тип задачи",
        description="Тип выполняемой задачи: создание файла(FILE_CREATE), копирование файла(FILE_COPY) и удаление файла(FILE_DELETE)",
    )
    source_path: str = Field(
        ...,
        title='Исходный путь файла',
        description="Исходный путь файла",
        min_length=1,
        example = "/app/files/file.txt"
    )
    destination_path: Optional[str] = Field(
        None,
        title='Целевой путь файла',
        description="Целевой путь для копирования ",
        min_length=1,
        example="/app/files/file1.txt"
    )



class UpdateTaskRequest(BaseModel):
    id:str = Field(
        ...,
        title="Идентификатор задачи",
        description="Уникальный идентификатор задачи в формате uuid",
    )
    name:Optional[str] = Field(
        None,
        min_length=1,
        title='Наименование задачи',
        description="Наименование задачи"
    )
    task_data: Optional[FileTaskDataUpdate] = Field(
        None
    )

class GetCancelTaskResponse(BaseModel):
    id:str = Field(
        ...,
        title="Идентификатор задачи",
        description="Уникальный идентификатор задачи в формате uuid",
    )
    status:TaskStatusEnum = Field(
        ...,
        title='Статус задачи',
        description="Статус задачи"
    )
    updated_at: datetime = Field(
        ...,
        title='Дата и время обновления задачи',
        description='Дата и время обновления задачи'
    )
    model_config = ConfigDict(from_attributes=True)

class CancelTaskRequest(BaseModel):
    id:str = Field(
        ...,
        title="Идентификатор задачи",
        description="Уникальный идентификатор задачи в формате uuid",
    )
    model_config = ConfigDict(from_attributes=True)