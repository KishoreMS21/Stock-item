from datetime import datetime

from pydantic import BaseModel


class SaleItemIn(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class SaleCreate(BaseModel):
    business_id: int
    customer: str | None = None
    items: list[SaleItemIn]


class SaleItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    business_id: int
    customer: str | None
    total: float
    sold_at: datetime
    items: list[SaleItemOut]

    class Config:
        from_attributes = True
