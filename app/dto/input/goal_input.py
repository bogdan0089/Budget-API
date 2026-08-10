from datetime import date
from pydantic import BaseModel, Field


class GoalCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: float = Field(gt=0, description="Target amount must be greater than 0")
    deadline: date | None = None


class GoalDepositDTO(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
