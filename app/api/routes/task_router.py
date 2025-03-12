from uuid import UUID
from fastapi_cache import FastAPICache
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, status,Path
from fastapi_cache.decorator import cache
from app.api.dependencies.task import get_task_repository
from app.api.exceptions.task import InternalServerException, NotFoundException, BadRequestException, ConflictException
from app.api.schemas.task import CreateTaskResponse, CreateTaskRequest, GetStateTaskResponse, GetTaskListRequest, \
    UpdateTaskRequest, GetCancelTaskResponse, CancelTaskRequest
from app.application.services.task_processor import TaskProcessor
from app.application.use_cases.cancel_task import CancelTaskUseCase
from app.application.use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.execute_task import ExecuteTaskUseCase
from app.application.use_cases.get_task_list import GetTaskListUseCase
from app.application.use_cases.get_task_status import GetTaskStatusUseCase
from app.application.use_cases.update_task import UpdateTaskUseCase
from app.domain.exceptions.entity import TaskException, TaskNotFoundException
from app.domain.exceptions.value_object import TaskTypeException
from app.infrastructure.repositories.postgres_task_repository import PostgresTaskRepository
from typing import Annotated, List
from app.infrastructure.workers.celery_worker import celery_app
from app.infrastructure.workers.tasks import enqueue_task_execution, enqueue_task_creation

router = APIRouter(prefix="/tasks", tags=["Tasks"])



@router.post(
    "/sync/create",
    response_model=CreateTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой задачи",
    description="Создает новую задачу",
    response_description="Возвращает данные о созданной задаче"
)
async def create_task_sync(
    task: CreateTaskRequest,
    repo: Annotated[PostgresTaskRepository, Depends(get_task_repository)]
)->CreateTaskResponse:
    """
    Создает задачу синхронно.
    Args:
        task (CreateTaskRequest): Данные новой задачи.
        repo (PostgresTaskRepository): Репозиторий для работы с задачами.
    Return:
        CreateTaskResponse: Созданная задача.
    Exception:
        BadRequestException: Если переданы некорректные данные.
        InternalServerException: Если произошла внутренняя ошибка.
    """
    try:
        use_case = CreateTaskUseCase(repo)
        new_task = await use_case.execute(
            name=task.name,
            data=task.task_data.dict()
        )
        enqueue_task_execution(new_task.id)
        await FastAPICache.clear()
        return new_task
    except TaskTypeException as e:
        raise BadRequestException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"Ошибка: {str(e)}")



@router.post(
    "/async/create",
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой задачи асинхронно",
    description="Создает новую задачу асинхронно",
    response_description="Возвращает данные о созданной задаче"
)
async def create_task_async(
    task: CreateTaskRequest
)->dict:
    """
    Создает задачу асинхронно через Celery.
    Args:
        task (CreateTaskRequest): Данные новой задачи.
    Return:
        dict: Информация о поставленной в очередь задаче.
    """
    task_id_celery = enqueue_task_creation(task.name, task.task_data.dict())
    await FastAPICache.clear()
    return {
        "task_id": task_id_celery,
        "status": "PENDING",
        "message": "Задача поставлена в очередь",
        "task_status_url": f"/async/task/result/{task_id_celery}"
    }



@router.get(
    "/id/{task_id}",
    response_model=GetStateTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение статуса задачи",
    description="Получает статус задачи",
    response_description="Возвращает данные о статусе задачи и результате выполнения(при наличии)"
)
@cache(expire=120)
async def get_state_task(
    task_id: Annotated[UUID,Path(...,title="Идентификатор задачи",description="Уникальный идентификатор задачи в формате uuid")],
    repo: Annotated[PostgresTaskRepository, Depends(get_task_repository)]
):
    """
    Получает статус задачи по её идентификатору.
    Args:
        task_id (UUID): Уникальный идентификатор задачи.
        repo (PostgresTaskRepository): Репозиторий для работы с задачами.
    Return:
        GetStateTaskResponse: Данные о задаче.
    Exception:
        BadRequestException: Некорректные данные.
        NotFoundException: Задача не найдена.
        ConflictException: Ошибка при получении данных.
        InternalServerException: Внутренняя ошибка.
    """
    try:
        use_case = GetTaskStatusUseCase(repo)
        task = await use_case.execute(
            task_id=task_id
        )
        return task
    except TaskTypeException as e:
        raise BadRequestException(detail=str(e))
    except TaskNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except TaskException as e:
        raise ConflictException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"Ошибка: {str(e)}")


@router.get("/list",
    status_code=status.HTTP_200_OK,
    response_model=List[CreateTaskResponse],
    summary="Получение списка задач",
    description="Возвращает список задач с возможностью фильтрации.",
    response_description="Возвращает список задач, соответствующих заданным фильтрам. Если задачи не найдены, вернется пустой список."
    )
@cache(expire=300)
async def get_tasks(
    repo: Annotated[PostgresTaskRepository, Depends(get_task_repository)],
    filters: GetTaskListRequest = Depends(),
):
    """
    Получает список задач с фильтрацией.
    Args:
        repo (PostgresTaskRepository): Репозиторий для работы с задачами.
        filters (GetTaskListRequest): Фильтры для поиска задач.
    Return:
        List[CreateTaskResponse]: Список задач.
    """
    try:
        use_case = GetTaskListUseCase(repo)
        tasks = await use_case.execute(
            name=filters.name,
            created_at_from=filters.created_at_from,
            created_at_to=filters.created_at_to,
            updated_at_from=filters.updated_at_from,
            updated_at_to=filters.updated_at_to,
            status=filters.status,
            task_type=filters.task_type
        )
        return tasks
    except Exception as e:
        raise InternalServerException(detail=f"Ошибка: {str(e)}")


@router.post(
    "/update",
    response_model=CreateTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление задачи",
    description="Обновляет данные задачи",
    response_description="Возвращает данные о обновленной задаче"
)
async def update_task(
    task: UpdateTaskRequest,
    repo: Annotated[PostgresTaskRepository, Depends(get_task_repository)]
)->CreateTaskResponse:
    """
    Обновляет данные существующей задачи.
    Args:
        task (UpdateTaskRequest): Данные для обновления задачи.
        repo (PostgresTaskRepository): Репозиторий для работы с задачами.
    Return:
        CreateTaskResponse: Обновленная задача.
    Exception:
        BadRequestException: Если переданы некорректные данные.
        NotFoundException: Если задача не найдена.
        ConflictException: Если обновление задачи невозможно.
        InternalServerException: Если произошла внутренняя ошибка.
    """
    try:
        use_case = UpdateTaskUseCase(repo)
        updated_task = await use_case.execute(
            task_id=task.id,
            name=task.name,
            data=task.task_data
        )
        await FastAPICache.clear()
        return updated_task
    except TaskTypeException as e:
        raise BadRequestException(detail=str(e))
    except TaskNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except TaskException as e:
        raise ConflictException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"Ошибка: {str(e)}")


@router.post(
    "/cancel",
    status_code=status.HTTP_200_OK,
    response_model=GetCancelTaskResponse,
    summary="Отмена задачи",
    description="Отменяет выполнение задачи",
    response_description="Возвращает данные о статусе задачи"
)
async def cancel_task(
    task:CancelTaskRequest,
    repo: Annotated[PostgresTaskRepository, Depends(get_task_repository)]
):
    """
    Отменяет выполнение задачи.
    Args:
        task (CancelTaskRequest): Идентификатор задачи для отмены.
        repo (PostgresTaskRepository): Репозиторий для работы с задачами.
    Return:
        GetCancelTaskResponse: Данные о статусе отмененной задачи.
    Exception:
        BadRequestException: Если переданы некорректные данные.
        NotFoundException: Если задача не найдена.
        ConflictException: Если отмена невозможна.
        InternalServerException: Если произошла внутренняя ошибка.
    """
    try:
        use_case = CancelTaskUseCase(repo)
        canceled_task = await use_case.execute(
            task_id=task.id
        )
        await FastAPICache.clear()
        return canceled_task
    except TaskTypeException as e:
        raise BadRequestException(detail=str(e))
    except TaskNotFoundException as e:
        raise NotFoundException(detail=str(e))
    except TaskException as e:
        raise ConflictException(detail=str(e))
    except Exception as e:
        raise InternalServerException(detail=f"Ошибка: {str(e)}")

@router.get("/async/task/result/{task_id}",
        status_code=status.HTTP_200_OK,
        summary="Получение состояния задачи отправленной в очередь",
        description="Получает состояние задачи отправленной в очередь",
        response_description="Возвращает данные о состоянии задачи отправленной в очередь"
            )
def get_task_result(
        task_id:Annotated[UUID,Path(...,title="Идентификатор задачи",description="Уникальный идентификатор задачи в формате uuid")]
):
    """
    Получает состояние задачи, отправленной в очередь Celery.
    Args:
        task_id (UUID): Уникальный идентификатор задачи.
    Return:
        dict: Данные о состоянии задачи.
    """
    task_result = AsyncResult(str(task_id), app=celery_app)
    if task_result.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING"}
    elif task_result.state == "SUCCESS":
        return task_result.result
    elif task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "FAILURE",
            "error": str(task_result.result)
        }
    else:
        return {"task_id": task_id, "status": task_result.state}