from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.categorize import categorize
from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Business, Expense, User
from app.models.expense import ExpenseCategory
from app.schemas import ExpenseCreate, ExpenseOut


router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def _verify_owner(db: Session, business_id: int, user: User) -> None:
    biz = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Expense]:
    _verify_owner(db, business_id, user)
    return db.query(Expense).filter(Expense.business_id == business_id).order_by(Expense.incurred_at.desc()).all()


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense(
    payload: ExpenseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Expense:
    _verify_owner(db, payload.business_id, user)
    data = payload.model_dump()
    if data.get("category") in (None, ExpenseCategory.OTHER):
        data["category"] = categorize(data.get("description"))
    expense = Expense(**data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
