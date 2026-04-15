from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    customer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    sold_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int]
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2))

    sale: Mapped["Sale"] = relationship(back_populates="items")
