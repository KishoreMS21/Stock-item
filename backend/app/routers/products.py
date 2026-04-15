from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Business, Product, User
from app.schemas import ProductCreate, ProductOut, ProductUpdate


router = APIRouter(prefix="/api/products", tags=["products"])


def _owned_business(db: Session, business_id: int, user: User) -> Business:
    biz = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")
    return biz


@router.get("", response_model=list[ProductOut])
def list_products(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Product]:
    _owned_business(db, business_id, user)
    return db.query(Product).filter(Product.business_id == business_id).all()


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    _owned_business(db, payload.business_id, user)
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    _owned_business(db, product.business_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product
