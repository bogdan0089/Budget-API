from uuid import UUID
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel


class GoalOutputDTO(BaseModel):
    uuid: UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    progress_percent: float
    deadline: date | None
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
