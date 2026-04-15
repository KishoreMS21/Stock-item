from pydantic import BaseModel


class ProductCreate(BaseModel):
    business_id: int
    sku: str
    name: str
    category: str | None = None
    unit_cost: float = 0
    unit_price: float = 0
    stock_on_hand: int = 0
    reorder_point: int = 0
    min_stock: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit_cost: float | None = None
    unit_price: float | None = None
    reorder_point: int | None = None
    min_stock: int | None = None


class ProductOut(BaseModel):
    id: int
    business_id: int
    sku: str
    name: str
    category: str | None
    unit_cost: float
    unit_price: float
    stock_on_hand: int
    reorder_point: int
    min_stock: int

    class Config:
        from_attributes = True
