import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.get_task_status import GetTaskStatusUseCase
from app.domain.entities.task import Task
from app.domain.exceptions.entity import TaskNotFoundException
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
async def test_get_task_status_success():
    """Проверяем успешное получение статуса задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)

    task = Task(
        id="123",
        name="Test Task",
        task_data=None,
        status=TaskStatusEnum.IN_PROGRESS,
        result="Processing...",
        updated_at="2024-03-12T12:00:00Z"
    )

    task_repository_mock.get_task_by_id.return_value = task

    use_case = GetTaskStatusUseCase(task_repository=task_repository_mock)

    result = await use_case.execute(task_id="123")

    assert result == {
        "id": "123",
        "status": TaskStatusEnum.IN_PROGRESS,
        "result": "Processing...",
        "updated_at": "2024-03-12T12:00:00Z"
    }

    task_repository_mock.get_task_by_id.assert_awaited_once_with("123")


@pytest.mark.asyncio
async def test_get_task_status_not_found():
    """Проверяем, что исключение TaskNotFoundException вызывается, если задачи не существует"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    task_repository_mock.get_task_by_id.return_value = None

    use_case = GetTaskStatusUseCase(task_repository=task_repository_mock)

    with pytest.raises(TaskNotFoundException, match="Задачи с таким ID - 123 не найдено."):
        await use_case.execute(task_id="123")

    task_repository_mock.get_task_by_id.assert_awaited_once_with("123")