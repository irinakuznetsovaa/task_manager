import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.create_task import CreateTaskUseCase
from app.domain.entities.task import Task
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum


@pytest.mark.asyncio
async def test_create_task_success():
    """Проверяем успешное создание задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    task_repository_mock.create_task = AsyncMock(side_effect=lambda task: task)  # Возвращаем сам Task

    use_case = CreateTaskUseCase(task_repository=task_repository_mock)

    # Данные для создания задачи
    name = "Test Task"
    data = {
        "task_type": TaskTypeEnum.FILE_CREATE.value,
        "source_path": "/tmp/source.txt",
        "destination_path": ""
    }

    # Вызов use-case
    created_task = await use_case.execute(name=name, data=data)

    # Проверки
    assert isinstance(created_task, Task)
    assert created_task.name == TaskName(name)
    assert created_task.status == TaskStatus(TaskStatusEnum.PENDING)
    assert isinstance(created_task.task_data, FileTaskData)
    assert created_task.task_data.task_type == TaskTypeEnum.FILE_CREATE
    assert created_task.task_data.source_path == "/tmp/source.txt"


    # Проверяем, что `create_task` был вызван 1 раз
    task_repository_mock.create_task.assert_called_once()


@pytest.mark.asyncio
async def test_create_task_invalid_type():
    """Проверяем ошибку при передаче неподдерживаемого типа задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    use_case = CreateTaskUseCase(task_repository=task_repository_mock)

    name = "Invalid Task"
    data = {
        "task_type": "INVALID_TASK_TYPE",
        "source_path": "/tmp/source.txt",
        "destination_path": "/tmp/destination.txt"
    }

    with pytest.raises(TaskTypeException, match="Неподдерживаемый тип задачи: INVALID_TASK_TYPE"):
        await use_case.execute(name=name, data=data)


    task_repository_mock.create_task.assert_not_called()