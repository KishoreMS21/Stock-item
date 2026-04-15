from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Business, User
from app.schemas import BusinessCreate, BusinessOut


router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessOut])
def list_businesses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Business]:
    return db.query(Business).filter(Business.owner_id == user.id).all()


@router.post("", response_model=BusinessOut, status_code=201)
def create_business(
    payload: BusinessCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    biz = Business(owner_id=user.id, name=payload.name, currency=payload.currency)
    db.add(biz)
    db.commit()
    db.refresh(biz)
    return biz
