import pytest
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.task import Task
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_data import TaskData
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from app.domain.value_objects.task_type import TaskTypeEnum


@dataclass(frozen=True)
class MockTaskData(TaskData):
    task_type: TaskTypeEnum


@pytest.fixture
def sample_task():
    """Создание тестовую задачу"""
    return Task(
        name=TaskName("Test Task"),
        task_data=MockTaskData(TaskTypeEnum.FILE_CREATE)
    )


def test_task_creation(sample_task):
    """Проверка на корректность создания задачи"""
    assert isinstance(sample_task.id, str)
    assert sample_task.name.value == "Test Task"
    assert sample_task.task_data.task_type == TaskTypeEnum.FILE_CREATE
    assert sample_task.status.value == TaskStatusEnum.PENDING
    assert sample_task.result.value == ""
    assert isinstance(sample_task.created_at, datetime)
    assert isinstance(sample_task.updated_at, datetime)


def test_update_status(sample_task):
    """Проверка на обновление статуса задачи"""
    sample_task.update_status(TaskStatus(TaskStatusEnum.IN_PROGRESS))
    assert sample_task.status.value == TaskStatusEnum.IN_PROGRESS
    assert sample_task.updated_at >= sample_task.created_at


def test_update_result(sample_task):
    """Проверка на обновление результата задачи"""
    sample_task.update_result(TaskResult("Success"))
    assert sample_task.result.value == "Success"
    assert sample_task.updated_at >= sample_task.created_at


def test_update_name(sample_task):
    """Проверка на обновление имени задачи"""
    new_name = TaskName("Updated Task")
    sample_task.update_name(new_name)
    assert sample_task.name.value == "Updated Task"
    assert sample_task.updated_at >= sample_task.created_at


def test_update_task_data(sample_task):
    """Проверка на обновление данных задачи"""
    new_data = MockTaskData(TaskTypeEnum.FILE_DELETE)
    sample_task.update_task_data(new_data)
    assert sample_task.task_data.task_type == TaskTypeEnum.FILE_DELETE
    assert sample_task.updated_at >= sample_task.created_at