from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    sku: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    stock_on_hand: Mapped[int] = mapped_column(default=0)
    reorder_point: Mapped[int] = mapped_column(default=0)
    min_stock: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    business: Mapped["Business"] = relationship(back_populates="products")
