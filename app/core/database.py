from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Создаем движок для работы с PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Базовый класс для моделей
Base = declarative_base()