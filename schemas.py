from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    is_important: bool = Field(..., description="Важность задачи")
    is_urgent: bool = Field(..., description="Срочность задачи")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Новое название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Новое описание")
    is_important: Optional[bool] = Field(None, description="Новая важность")
    is_urgent: Optional[bool] = Field(None, description="Новая срочность")
    completed: Optional[bool] = Field(None, description="Статус выполнения")

    @field_validator("title", "is_important", "is_urgent", "completed")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Поле не может быть null")
        return value


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный идентификатор задачи", examples=[1])
    quadrant: str = Field(..., description="Квадрант матрицы Эйзенхауэра", examples=["Q1"])
    completed: bool = Field(False, description="Статус выполнения задачи")
    created_at: datetime = Field(..., description="Дата и время создания задачи")
    completed_at: Optional[datetime] = Field(None, description="Дата и время выполнения задачи")
