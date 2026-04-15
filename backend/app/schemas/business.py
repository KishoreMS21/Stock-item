from pydantic import BaseModel


class BusinessCreate(BaseModel):
    name: str
    currency: str = "USD"


class BusinessOut(BaseModel):
    id: int
    name: str
    currency: str

    class Config:
        from_attributes = True
