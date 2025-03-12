from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete,and_

from app.domain.entities.task import Task
from app.domain.exceptions.value_object import TaskTypeException
from app.domain.repositories.task_repository import TaskRepository
from app.domain.value_objects.file_task_data import FileTaskData
from app.domain.value_objects.task_name import TaskName
from app.domain.value_objects.task_result import TaskResult
from app.domain.value_objects.task_status import TaskStatusEnum, TaskStatus
from app.domain.value_objects.task_type import TaskTypeEnum
from app.infrastructure.models.task_model import TaskModel


@dataclass
class PostgresTaskRepository(TaskRepository):
    """
    Репозиторий задач для работы с PostgreSQL.
    """
    session: AsyncSession

    async def create_task(self, task: Task) -> Task:
        """
        Создает новую задачу в базе данных.

        Args:
            task (Task): Объект задачи.

        Return:
            Task: Созданная задача.
        """
        task_model = TaskModel(
            id=task.id,
            name=task.name.as_generic_type(),
            task_data=task.task_data.as_generic_type(),
            status=task.status.as_generic_type(),
            result=task.result.as_generic_type(),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        self.session.add(task_model)
        await self.session.commit()
        await self.session.refresh(task_model)
        return await self.get_task_by_id(task_model.id)

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Получает задачу по ее идентификатору.

        Args:
            task_id (str): Идентификатор задачи.

        Return:
            Optional[Task]: Найденная задача или None, если не найдена.
        """
        get_task=select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(get_task)
        task_model = result.scalar_one_or_none()
        if task_model:
            return self._map_to_domain(task_model)
        else:
            return None

    async def get_tasks(
        self,
        name: Optional[TaskName] = None,
        created_at_from:Optional[datetime]=None,
        created_at_to:Optional[datetime]=None,
        updated_at_from: Optional[datetime] = None,
        updated_at_to: Optional[datetime] = None,
        status: Optional[TaskStatusEnum] = None,
        task_type: Optional[TaskTypeEnum] = None
    ) -> List[Task]:
        """
        Получает список задач с возможными фильтрами.

        Args:
            name (Optional[TaskName]): Фильтр по имени.
            created_at_from (Optional[datetime]): Фильтр по дате создания (от).
            created_at_to (Optional[datetime]): Фильтр по дате создания (до).
            updated_at_from (Optional[datetime]): Фильтр по дате обновления (от).
            updated_at_to (Optional[datetime]): Фильтр по дате обновления (до).
            status (Optional[TaskStatusEnum]): Фильтр по статусу.
            task_type (Optional[TaskTypeEnum]): Фильтр по типу задачи.

        Return:
            List[Task]: Список найденных задач.
        """
        query = select(TaskModel)
        filters = []
        if name:
            filters.append(TaskModel.name.ilike(f"%{name}%"))
        if status:
            filters.append(TaskModel.status == status)
        if task_type:
            filters.append(TaskModel.task_data["task_type"].as_string() == task_type.value)
        if created_at_from:
            filters.append(TaskModel.created_at >= created_at_from)
        if created_at_to:
            filters.append(TaskModel.created_at <= created_at_to)
        if updated_at_from:
            filters.append(TaskModel.updated_at >= updated_at_from)
        if updated_at_to:
            filters.append(TaskModel.updated_at <= updated_at_to)
        if filters:
            query = query.filter(and_(*filters))

        result = await self.session.execute(query)
        task_models = result.scalars().all()
        return [self._map_to_domain(task) for task in task_models]

    async def update_task(self, task: Task) -> Task:
        """
         Обновляет информацию о задаче.

         Args:
             task (Task): Обновленный объект задачи.

         Return:
             Task: Обновленный объект задачи.
         """
        await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == task.id)
            .values(
                name=task.name,
                status=task.status,
                task_data=task.task_data,
                updated_at=task.updated_at,
                result=task.result
            )
        )
        await self.session.commit()
        return await self.get_task_by_id(task.id)

    async def delete_task(self, task_id: str) -> None:
        """
        Удаляет задачу по ее идентификатору.

        Args:
            task_id (str): Идентификатор задачи.

        Return:
            None
        """
        await self.session.execute(delete(TaskModel).where(TaskModel.id == task_id))
        await self.session.commit()

    def _map_to_domain(self, task_model: TaskModel) -> Task:
        """
        Преобразует объект базы данных в объект доменной модели.

        Args:
            task_model (TaskModel): Объект модели базы данных.

        Return:
            Task: Объект доменной модели.

        Exception:
            TaskTypeException: Если тип задачи не поддерживается.
        """
        task_type_enum = TaskTypeEnum(task_model.task_data['task_type'])
        if task_type_enum in [TaskTypeEnum.FILE_CREATE, TaskTypeEnum.FILE_COPY, TaskTypeEnum.FILE_DELETE]:
            task_data = FileTaskData(
                task_type=task_type_enum,
                source_path=task_model.task_data['source_path'],
                destination_path=task_model.task_data.get('destination_path')
            ).as_generic_type()
        else:
            raise TaskTypeException(message=f"Неподдерживаемый тип задачи: {task_type_enum}")

        return Task(
            id=str(task_model.id),
            name=TaskName(task_model.name).as_generic_type(),
            task_data=task_data,
            status=TaskStatus(task_model.status).as_generic_type(),
            result=TaskResult(task_model.result).as_generic_type(),
            created_at=task_model.created_at,
            updated_at=task_model.updated_at,
        )
