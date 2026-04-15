from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models import Business, Product, Sale, SaleItem, User
from app.models.inventory import InventoryMovement, MovementType
from app.schemas import SaleCreate, SaleOut


router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.get("", response_model=list[SaleOut])
def list_sales(
    business_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Sale]:
    biz = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")
    return db.query(Sale).filter(Sale.business_id == business_id).order_by(Sale.sold_at.desc()).all()


@router.post("", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Sale:
    biz = db.query(Business).filter(
        Business.id == payload.business_id, Business.owner_id == user.id
    ).first()
    if not biz:
        raise HTTPException(404, "Business not found")

    total = 0.0
    sale = Sale(business_id=payload.business_id, customer=payload.customer, total=0)
    db.add(sale)
    db.flush()

    for item in payload.items:
        product = db.query(Product).filter(
            Product.id == item.product_id, Product.business_id == payload.business_id
        ).first()
        if not product:
            raise HTTPException(400, f"Product {item.product_id} not found")
        if product.stock_on_hand < item.quantity:
            raise HTTPException(400, f"Insufficient stock for {product.sku}")
        product.stock_on_hand -= item.quantity
        db.add(SaleItem(
            sale_id=sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))
        db.add(InventoryMovement(
            product_id=item.product_id,
            movement_type=MovementType.OUT,
            quantity=item.quantity,
            reason=f"sale #{sale.id}",
        ))
        total += item.quantity * item.unit_price

    sale.total = total
    db.commit()
    db.refresh(sale)
    return sale
