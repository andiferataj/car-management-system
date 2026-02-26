from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.car import Car
from models.user import User

router = APIRouter(prefix="/cars", tags=["Cars"])


class CarCreate(BaseModel):
    name:    str
    brand:   str
    serie:   str
    year:    int
    user_id: Optional[int] = None


class CarUpdate(BaseModel):
    name:    Optional[str] = None
    brand:   Optional[str] = None
    serie:   Optional[str] = None
    year:    Optional[int] = None
    user_id: Optional[int] = None


def car_to_dict(c: Car) -> dict:
    return {
        "id":         c.id,
        "name":       c.name,
        "brand":      c.brand,
        "serie":      c.serie,
        "year":       c.year,
        "user_id":    c.user_id,
        "owner_name": c.owner.name if c.owner else None
    }


# CREATE
@router.post("/", status_code=201)
def create_car(payload: CarCreate, db: Session = Depends(get_db)):
    if payload.user_id and not db.query(User).filter(User.id == payload.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    car = Car(**payload.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return {"message": "Car created successfully", "id": car.id}


# READ ALL
@router.get("/")
def get_all_cars(
    brand:   Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Car)
    if brand:   query = query.filter(Car.brand.ilike(f"%{brand}%"))
    if user_id: query = query.filter(Car.user_id == user_id)
    cars = query.order_by(Car.brand).all()
    return {"total": len(cars), "cars": [car_to_dict(c) for c in cars]}


# READ ONE
@router.get("/{car_id}")
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car_to_dict(car)


# UPDATE
@router.put("/{car_id}")
def update_car(car_id: int, payload: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if payload.user_id and not db.query(User).filter(User.id == payload.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(car, field, value)
    db.commit()
    return {"message": "Car updated successfully"}


# DELETE
@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully"}
