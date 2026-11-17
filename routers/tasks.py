from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


# Временное хранилище задач
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]


# 2. Получение списка всех задач
@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),
        "tasks": tasks_db
    }


# 3. Фильтрация задач по квадранту
@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:

    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )

    filtered_tasks = [
        task
        for task in tasks_db
        if task["quadrant"] == quadrant
    ]

    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }


# 4. Получение статистики по задачам
@router.get("/stats")
async def get_tasks_stats() -> dict:

    # Количество задач в каждом квадранте
    by_quadrant = {
        quadrant: sum(
            1 for task in tasks_db
            if task["quadrant"] == quadrant
        )
        for quadrant in ["Q1", "Q2", "Q3", "Q4"]
    }

    # Количество выполненных и невыполненных задач
    by_status = {
        "completed": sum(
            1 for task in tasks_db
            if task["completed"]
        ),
        "pending": sum(
            1 for task in tasks_db
            if not task["completed"]
        )
    }

    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }


# 5. Фильтрация задач по статусу выполнения
@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:

    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=404,
            detail="Статус не найден"
        )

    # Преобразование статуса в булево значение
    is_completed = status == "completed"

    filtered_tasks = [
        task
        for task in tasks_db
        if task["completed"] == is_completed
    ]

    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }


# 6. Поиск задач по ключевому слову
@router.get("/search")
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:

    q = q.strip()

    if len(q) < 2:
        raise HTTPException(
            status_code=422,
            detail="Поисковый запрос должен содержать минимум 2 символа"
        )

    search_query = q.lower()

    filtered_tasks = [
        task
        for task in tasks_db
        if search_query in task["title"].lower()
        or search_query in (task["description"] or "").lower()
    ]

    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail="Задачи по данному запросу не найдены"
        )

    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }


# 7. Получение задачи по ID
# Динамический маршрут обязательно располагается в конце
@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:

    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )
