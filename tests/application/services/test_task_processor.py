import pytest
import os
import shutil
from pathlib import Path
from app.application.services.task_processor import TaskProcessor
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_type import TaskTypeEnum
from app.domain.exceptions.entity import TaskProcessingException

@pytest.fixture
def temp_dir(tmp_path):
    """Создает временную директорию для файлов"""
    return tmp_path

@pytest.fixture
def temp_file(temp_dir):
    """Создает временный файл"""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("test content")
    return file_path

@pytest.mark.asyncio
async def test_create_file(temp_dir):
    processor = TaskProcessor()
    file_path = temp_dir / "new_file.txt"

    file_data = FileTaskData(task_type=TaskTypeEnum.FILE_CREATE, source_path=str(file_path))
    await processor.create_file(file_data)

    assert file_path.exists()

@pytest.mark.asyncio
async def test_copy_file(temp_file, temp_dir):
    processor = TaskProcessor()
    dest_path = temp_dir / "copied_file.txt"

    file_data = FileTaskData(
        task_type=TaskTypeEnum.FILE_COPY,
        source_path=str(temp_file),
        destination_path=str(dest_path)
    )
    await processor.copy_file(file_data)

    assert dest_path.exists()
    assert dest_path.read_text() == "test content"

@pytest.mark.asyncio
async def test_delete_file(temp_file):
    processor = TaskProcessor()
    file_data = FileTaskData(task_type=TaskTypeEnum.FILE_DELETE, source_path=str(temp_file))

    await processor.delete_file(file_data)

    assert not temp_file.exists()

@pytest.mark.asyncio
async def test_copy_nonexistent_file(temp_dir):
    processor = TaskProcessor()
    non_existent = temp_dir / "non_existent.txt"
    dest_path = temp_dir / "destination.txt"

    file_data = FileTaskData(
        task_type=TaskTypeEnum.FILE_COPY,
        source_path=str(non_existent),
        destination_path=str(dest_path),
    )

    with pytest.raises(TaskProcessingException, match="Ошибка при копировании"):
        await processor.copy_file(file_data)