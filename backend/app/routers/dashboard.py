from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Business, User
from app.schemas import DashboardOut
from app.services.dashboard import build_dashboard


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardOut:
    biz = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")
    return build_dashboard(db, business_id)
