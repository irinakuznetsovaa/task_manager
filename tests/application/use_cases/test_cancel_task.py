import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.cancel_task import CancelTaskUseCase
from app.domain.exceptions.entity import TaskNotFoundException
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.value_objects.task_status import TaskStatusEnum
from app.domain.entities.task import Task


@pytest.mark.asyncio
async def test_cancel_task_success():
    """Проверяем успешную отмену задачи со статусом PENDING"""

    task_repository_mock = AsyncMock()

    # Создаем мок задачи и явно задаем изменение статуса
    task = AsyncMock()
    task.status = TaskStatusEnum.PENDING

    async def update_task_side_effect(updated_task):
        updated_task.status = TaskStatusEnum.CANCELED
        return updated_task

    task_repository_mock.get_task_by_id.return_value = task
    task_repository_mock.update_task.side_effect = update_task_side_effect  # Фиксируем изменение

    use_case = CancelTaskUseCase(task_repository=task_repository_mock)

    result = await use_case.execute("task_id")

    assert result["status"] == TaskStatusEnum.CANCELED, f"Expected CANCELED, got {result['status']}"
    task_repository_mock.update_task.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_task_invalid_status():
    """Ошибка при попытке отменить задачу, которая уже выполняется"""

    task_repository_mock = AsyncMock()
    task = AsyncMock()
    task.status = TaskStatusEnum.IN_PROGRESS  # Нельзя отменять выполняющуюся задачу

    task_repository_mock.get_task_by_id.return_value = task

    use_case = CancelTaskUseCase(task_repository=task_repository_mock)

    with pytest.raises(TaskTypeException, match="Отмена задачи с статусом - IN_PROGRESS невозможна"):
        await use_case.execute("task_id")


@pytest.mark.asyncio
async def test_cancel_task_not_found():
    """Ошибка, если задачи с таким ID не существует"""

    task_repository_mock = AsyncMock()
    task_repository_mock.get_task_by_id.return_value = None  # Задачи нет в БД

    use_case = CancelTaskUseCase(task_repository=task_repository_mock)

    with pytest.raises(TaskNotFoundException, match="Задачи с таким ID - task_id не найдено."):
        await use_case.execute("task_id")