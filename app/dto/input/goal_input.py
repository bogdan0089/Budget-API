from datetime import date
from pydantic import BaseModel, Field


class GoalCreateDTO(BaseModel):
    name: str
    target_amount: float = Field(gt=0, description="Target amount must be greater than 0")
    deadline: date | None = None


class GoalDepositDTO(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")
