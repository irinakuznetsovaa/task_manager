# Task Manager


Task Manager — это сервис управления задачами, реализованный на FastAPI с поддержкой Celery, Redis, RabbitMQ, PostgreSQL,Grafana, Prometheus и Docker.

## Функционал

- Создание задачи (синхронно через API и асинхронно через очередь сообщений)
- Получение статуса задачи
- Получение списка задач с фильтрацией
- Обновление задачи
- Отмена выполнения задачи
- Асинхронная обработка задач с помощью Celery
- Базовое кеширование результатов с помощью Redis
- Мониторинг с Prometheus+Grafana+PostgreSQL


## Технологии

- FastAPI
- SQLAlchemy 
- PostgreSQL 
- Celery 
- Redis 
- RabbitMQ
- Docker
- Prometheus
- Grafana

## Установка и запуск
### 1.Клонируйте репозиторий

```sh
git clone https://github.com/irinakuznetsovaa/task_manager.git
сd task_manager
```

### 2.Создайте и настройте .env

Создай файл .env в корне проекта, скопируй туда переменные окружения из .env.example и настрой их.
### 3. Запускаем через Docker

```sh
docker-compose up --build -d
```
После запуска:

FastAPI будет доступен по http://localhost:8000
Документация OpenAPI — http://localhost:8000/docs
Grafana - http://localhost:3000/ (логин,пароль:admin)
Prometheus -http://localhost:9090/

## API Документация
После запуска можно открыть документацию API:
Swagger UI: http://localhost:8000/docs

#### Основные эндпоинты

### 📌 Основные эндпоинты API

| **Метод** | **URL**                        | **Описание**                                      |
|-----------|--------------------------------|--------------------------------------------------|
| **POST**  | `/tasks/sync/create`          | Создать задачу (синхронно)                       |
| **POST**  | `/tasks/async/create`         | Создать задачу (асинхронно через Celery)        |
| **GET**   | `/tasks/id/{task_id}`         | Получить статус задачи                           |
| **GET**   | `/tasks/list`                 | Получить список задач                           |
| **POST**  | `/tasks/update`               | Обновить задачу                                 |
| **POST**  | `/tasks/cancel`               | Отменить задачу                                 |
| **GET**   | `/async/task/result/{task_id}` | Получить результат выполнения асинхронной задачи           |




## Тестирование

### 1. Запускаем контейнер Docker

```sh
docker exec -it task_manager-app-1 /bin/sh
```
### 2.Команда:
```sh
pytest
```

