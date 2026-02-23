from pydantic import BaseModel, Field
from typing import Optional

class BrandBase(BaseModel):
    name: str = Field(..., min_length=1)

class Brand(BrandBase):
    id: str

    class Config:
        orm_mode = True

class CarModelBase(BaseModel):
    brand_id: str
    name: str
    year: Optional[int]

class CarModel(CarModelBase):
    id: str

    class Config:
        orm_mode = True

class CarBase(BaseModel):
    model_id: str
    vin: Optional[str]
    color: Optional[str]
    price: Optional[float]
    status: Optional[str] = "available"

class Car(CarBase):
    id: str

    class Config:
        orm_mode = True
