from fastapi import APIRouter
from database import tasks_db


router = APIRouter(prefix="/stats", tags=["stats"])


# 4. Получение статистики по задачам
@router.get("/")
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
