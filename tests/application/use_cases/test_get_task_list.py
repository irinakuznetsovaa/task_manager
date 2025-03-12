import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from app.application.use_cases.get_task_list import GetTaskListUseCase
from app.domain.entities.task import Task
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum
from app.domain.repositories.task_repository import TaskRepository

@pytest.mark.asyncio
async def test_get_task_list_success():
    """Проверяем успешное получение списка задач с фильтрацией"""

    task_repository_mock = AsyncMock(spec=TaskRepository)

    tasks = [
        Task(
            id="1",
            name="Task 1",
            task_data=None,
            status=TaskStatusEnum.PENDING,
            result=None
        ),
        Task(
            id="2",
            name="Task 2",
            task_data=None,
            status=TaskStatusEnum.COMPLETED,
            result=None
        ),
    ]

    task_repository_mock.get_tasks.return_value = tasks

    use_case = GetTaskListUseCase(task_repository=task_repository_mock)

    result = await use_case.execute(
        name=TaskName("Task"),
        created_at_from=datetime(2024, 1, 1),
        created_at_to=datetime(2024, 12, 31),
        status=TaskStatusEnum.PENDING
    )

    assert result == tasks
    task_repository_mock.get_tasks.assert_awaited_once_with(
        name=TaskName("Task"),
        created_at_from=datetime(2024, 1, 1),
        created_at_to=datetime(2024, 12, 31),
        updated_at_from=None,
        updated_at_to=None,
        status=TaskStatusEnum.PENDING,
        task_type=None
    )