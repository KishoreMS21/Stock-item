from datetime import datetime

from pydantic import BaseModel

from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    business_id: int
    amount: float
    category: ExpenseCategory = ExpenseCategory.OTHER
    description: str | None = None


class ExpenseOut(BaseModel):
    id: int
    business_id: int
    amount: float
    category: ExpenseCategory
    description: str | None
    incurred_at: datetime

    class Config:
        from_attributes = True
