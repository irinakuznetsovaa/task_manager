from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.infrastructure.repositories.postgres_task_repository import PostgresTaskRepository

def get_task_repository(db: AsyncSession = Depends(get_db)):
    return PostgresTaskRepository(db)