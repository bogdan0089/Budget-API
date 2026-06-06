from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field


class BudgetCreateDTO(BaseModel):
    category_id: UUID
    month: date
    limit_amount: float = Field(gt=0, description="Limit must be greater than 0")


class BudgetUpdateDTO(BaseModel):
    limit_amount: float = Field(gt=0, description="Limit must be greater than 0")
