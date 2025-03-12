from app.application.services.task_processor import TaskProcessor
from app.application.use_cases.execute_task import ExecuteTaskUseCase
from app.domain.exceptions.entity import TaskProcessingException, TaskNotFoundException
from app.domain.exceptions.value_object import TaskStatusException, ValidationException
from app.infrastructure.workers.asyncio_service import run_async_function
from app.infrastructure.repositories.postgres_task_repository import PostgresTaskRepository
from app.application.use_cases.create_task import CreateTaskUseCase
from app.core.database import async_session_maker

from app.infrastructure.workers.celery_worker import celery_app


@celery_app.task(name="create_task",bind=True)
def create_task_in_db(self,name: str, task_data:dict):
    """
    Асинхронное создание задачи в базе данных через RabbitMQ.

    Args:
        name (str): Имя задачи.
        task_data (dict): Данные задачи.

    Return:
        dict: Информация о созданной задаче.
    """

    async def async_create():
        async with async_session_maker() as session:
            task_repo = PostgresTaskRepository(session)
            use_case = CreateTaskUseCase(task_repo)
            return await use_case.execute(name, task_data)

    try:
        new_task = run_async_function(async_create())
        enqueue_task_execution(new_task.id)
        return {
            "task_id": self.request.id,
            "db_task_id": new_task.id,
            "task_id_task_execute": new_task.id,
            "status": "SUCCESS"
        }
    except Exception as e:
        if hasattr(self, "update_state"):
            self.update_state(
                state="FAILURE",
                meta={
                    "exc_type": type(e).__name__,
                    "exc_message": str(e)
                }
            )
        raise


@celery_app.task(
    name="execute_task",
    bind=True,
    autoretry_for=(TaskProcessingException,),
    retry_kwargs={'max_retries':3, 'countdown':10}
)
def execute_task_celery(self,task_id: str):
    """
    Запускает выполнение задачи по ID через Celery.

    Args:
        task_id (str): Идентификатор задачи.

    Return:
        dict: Информация о статусе выполнения задачи.

    Exception:
        TaskNotFoundException: Если задача не найдена.
        TaskStatusException: Если статус задачи недопустим.
        ValidationException: Если валидация не пройдена.
        TaskProcessingException: Если произошла ошибка обработки.
    """

    async def async_execute():
        async with async_session_maker() as session:
            task_repo = PostgresTaskRepository(session)
            task_processor = TaskProcessor()
            use_case = ExecuteTaskUseCase(task_repo, task_processor)

            try:
                is_last_attempt = self.request.retries >= self.max_retries
                task= await use_case.execute(
                    task_id=task_id,
                    is_retry=self.request.retries > 0,
                    is_last_attempt=is_last_attempt,
                    is_celery=True
                    )
                # return {"status": "SUCCESS", "message": "Задача выполнена успешно"}
            except (TaskNotFoundException, TaskStatusException, ValidationException) as e:
                error_data = {
                    "exc_type": type(e).__name__,
                    "exc_message": str(e)
                }
                if hasattr(self, "update_state"):
                    self.update_state(state="FAILURE", meta=error_data)
                raise

            except TaskProcessingException as e:
                if self.request.retries < self.max_retries:
                    raise self.retry(exc=e, countdown=5)

                raise

    try:
        run_async_function(async_execute())
        return {
            "task_id": self.request.id,
            "status": "SUCCESS"
        }
    except Exception as e:
        error_data = {
            "exc_type": type(e).__name__,
            "exc_message": str(e)
        }
        if hasattr(self, "update_state"):
            self.update_state(state="FAILURE", meta=error_data)
        raise



def enqueue_task_creation(name: str, task_data:dict):
    """
    Отправляет команду на создание задачи в Celery через RabbitMQ.

    Args:
        name (str): Имя задачи.
        task_data (dict): Данные задачи.

    Return:
        str: Идентификатор задачи в Celery.
    """
    task = create_task_in_db.delay(name, task_data)
    return task.id


def enqueue_task_execution(task_id: str):
    """
    Отправляет задачу в Celery на выполнение.

    Args:
        task_id (str): Идентификатор задачи.

    Return:
        str: Идентификатор задачи в Celery.
    """
    task = execute_task_celery.apply_async(args=[task_id], task_id=task_id)
    return task.id