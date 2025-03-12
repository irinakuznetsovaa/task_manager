import pytest
from httpx import AsyncClient
from app.domain.value_objects.task_status import TaskStatus, TaskStatusEnum

@pytest.mark.asyncio
async def test_create_task_sync(ac: AsyncClient):
    """Тест создания задачи """
    task_data = {
        "name": "Test Task",
        "task_data": {
            "task_type": "FILE_CREATE",
            "source_path": "/app/files/test.txt",
            "destination_path": ""
        }
    }
    response = await ac.post("/tasks/sync/create", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == task_data["name"]
    assert data["status"] == "PENDING"

@pytest.mark.asyncio
async def test_get_task_status(ac: AsyncClient):
    """Тест получения статуса задачи"""

    task_data = {
        "name": "Status Check Task",
        "task_data": {
            "task_type": "FILE_CREATE",
            "source_path": "/app/files/test1.txt"
        }
    }
    create_response = await ac.post("/tasks/sync/create", json=task_data)
    task_id = create_response.json()["id"]


    response = await ac.get(f"/tasks/id/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] in ["PENDING", "IN_PROGRESS", "COMPLETED"]

@pytest.mark.asyncio
async def test_get_task_list(ac: AsyncClient):
    response = await ac.get("/tasks/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_task(ac: AsyncClient):
    """Тест обновления задачи"""
    task_data = {
        "name": "Update Test",
        "task_data": {
            "task_type": "FILE_CREATE",
            "source_path": "/app/files/test.txt"
        }
    }
    create_response = await ac.post("/tasks/sync/create", json=task_data)
    task_id = create_response.json()["id"]

    update_data = {
        "id": task_id,
        "name": "Updated Task Name",
        "task_data": {
            "task_type": "FILE_CREATE",
            "source_path": "/app/files/test2.txt"
        }
    }
    response = await ac.get(f"/tasks/id/{task_id}")
    data = response.json()
    if data["status"] != TaskStatus(TaskStatusEnum.PENDING):
        response = await ac.post("/tasks/update", json=update_data)
        assert response.status_code == 400
    else:
        response = await ac.post("/tasks/update", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Task Name"
        assert data["task_data"]["task_type"] == "FILE_DELETE"

@pytest.mark.asyncio
async def test_cancel_task(ac: AsyncClient):
    """Тест отмены задачи"""
    # Создаем задачу
    task_data = {
        "name": "Cancel Test",
        "task_data": {
            "task_type": "FILE_CREATE",
            "source_path": "/app/files/test2.txt"
        }
    }
    create_response = await ac.post("/tasks/sync/create", json=task_data)
    data=create_response.json()
    task_id = data["id"]
    cancel_data = {"id": task_id}
    response = await ac.get(f"/tasks/id/{task_id}")
    data = response.json()
    if data["status"] != TaskStatus(TaskStatusEnum.PENDING):
        response = await ac.post("/tasks/cancel", json=cancel_data)
        assert response.status_code == 400
    else:
        response = await ac.post("/tasks/cancel", json=cancel_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["status"] == "CANCELED"
