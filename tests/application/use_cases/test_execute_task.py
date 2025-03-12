import pytest
from unittest.mock import AsyncMock
from app.domain.entities.task import Task
from app.application.services.task_processor import TaskProcessor
from app.application.use_cases.execute_task import ExecuteTaskUseCase
from app.domain.exceptions.entity import TaskProcessingException
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum


@pytest.mark.asyncio
async def test_execute_task_success():
    """Проверяем успешное выполнение задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    task_processor_mock = AsyncMock(spec=TaskProcessor)

    task_id = "123"
    task = Task(
        id=task_id,
        name="Test Task",
        task_data={
            "task_type": TaskTypeEnum.FILE_CREATE,
            "source_path": "/tmp/source.txt",
            "destination_path": ""
        },
        status=TaskStatusEnum.PENDING,
        result=None
    )

    task_repository_mock.get_task_by_id.return_value = task
    task_repository_mock.update_task.return_value = task
    task_processor_mock.create_file.return_value = None

    use_case = ExecuteTaskUseCase(task_repository=task_repository_mock, task_processor=task_processor_mock)

    result = await use_case.execute(task_id=task_id)

    assert result.status == TaskStatusEnum.COMPLETED


@pytest.mark.asyncio
async def test_execute_task_processing_error():
    """Проверяем обработку ошибки во время выполнения задачи"""

    task_repository_mock = AsyncMock(spec=TaskRepository)
    task_processor_mock = AsyncMock(spec=TaskProcessor)

    task = Task(
        id="123",
        name="Test Task",
        task_data={
            "task_type": TaskTypeEnum.FILE_CREATE,
            "source_path": "/tmp/source.txt",
            "destination_path": ""
        },
        status=TaskStatusEnum.PENDING,
        result=None
    )

    task_repository_mock.get_task_by_id.return_value = task
    task_repository_mock.update_task.return_value = task
    task_processor_mock.create_file.side_effect = TaskProcessingException("Ошибка при создании файла")

    use_case = ExecuteTaskUseCase(task_repository=task_repository_mock, task_processor=task_processor_mock)

    with pytest.raises(TaskProcessingException) as exc_info:
        await use_case.execute(task_id="123")

    assert "Ошибка при создании файла" in str(exc_info.value)