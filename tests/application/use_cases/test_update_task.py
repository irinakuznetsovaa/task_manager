from types import SimpleNamespace

import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.update_task import UpdateTaskUseCase
from app.domain.entities.task import Task
from app.domain.exceptions.entity import TaskException, TaskNotFoundException
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.task_type import TaskTypeEnum


@pytest.mark.asyncio
async def test_update_task_success():
    """Проверяем успешное обновление задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)

    task = Task(
        id="123",
        name="Old Task Name",
        task_data=FileTaskData(
            task_type=TaskTypeEnum.FILE_CREATE,
            source_path="/old/source.txt",
            destination_path=""
        ),
        status=TaskStatusEnum.PENDING,
        result=None
    )

    updated_task = Task(
        id="123",
        name="New Task Name",
        task_data=FileTaskData(
            task_type=TaskTypeEnum.FILE_DELETE,
            source_path="/new/source.txt",
            destination_path=""
        ),
        status=TaskStatusEnum.PENDING,
        result=None
    )

    task_repository_mock.get_task_by_id.return_value = task
    task_repository_mock.update_task.return_value = updated_task

    use_case = UpdateTaskUseCase(task_repository=task_repository_mock)

    result = await use_case.execute(
        task_id="123",
        name="New Task Name",
        data=SimpleNamespace(
            task_type="FILE_DELETE",
            source_path="/new/source.txt",
            destination_path=""
        )
    )

    assert result.id == "123"
    assert result.name == "New Task Name"
    assert result.task_data.task_type == TaskTypeEnum.FILE_DELETE
    assert result.task_data.source_path == "/new/source.txt"


@pytest.mark.asyncio
async def test_update_task_not_found():
    """Проверяем, что исключение TaskNotFoundException вызывается, если задачи не существует"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    task_repository_mock.get_task_by_id.return_value = None

    use_case = UpdateTaskUseCase(task_repository=task_repository_mock)

    with pytest.raises(TaskNotFoundException, match="Задачи с таким ID - 123 не найдено."):
        await use_case.execute(task_id="123", name="New Name")

    task_repository_mock.get_task_by_id.assert_awaited_once_with("123")
    task_repository_mock.update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_invalid_status():
    """Проверяем, что исключение TaskException вызывается при попытке обновить задачу в неправильном статусе"""

    task_repository_mock = AsyncMock(spec=TaskRepository)

    task = Task(
        id="123",
        name="Old Task Name",
        task_data=None,
        status=TaskStatusEnum.IN_PROGRESS,
        result=None
    )

    task_repository_mock.get_task_by_id.return_value = task

    use_case = UpdateTaskUseCase(task_repository=task_repository_mock)

    with pytest.raises(TaskTypeException, match="Обновление задачи с статусом - IN_PROGRESS невозможно"):
        await use_case.execute(task_id="123", name="New Name")

    task_repository_mock.get_task_by_id.assert_awaited_once_with("123")
    task_repository_mock.update_task.assert_not_awaited()