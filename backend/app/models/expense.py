from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExpenseCategory(str, PyEnum):
    OPERATIONS = "operations"
    MARKETING = "marketing"
    INVENTORY = "inventory"
    SALARIES = "salaries"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory), default=ExpenseCategory.OTHER)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    incurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
