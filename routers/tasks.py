from fastapi import APIRouter, HTTPException, Query, Response, status
from datetime import datetime

from database import tasks_db
from schemas import TaskCreate, TaskUpdate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


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
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:

    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate) -> TaskResponse:
    if task.is_important and task.is_urgent:
        quadrant = "Q1"
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"
    else:
        quadrant = "Q4"

    new_id = max((task["id"] for task in tasks_db), default=0) + 1
    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now(),
        "completed_at": None,
    }
    tasks_db.append(new_task)
    return new_task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value

    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"
        else:
            task["quadrant"] = "Q4"

    if "completed" in update_data:
        task["completed_at"] = datetime.now() if task["completed"] else None
    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task["completed"] = True
    task["completed_at"] = datetime.now()
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
